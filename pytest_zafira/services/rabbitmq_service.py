import logging
import threading
import json
from datetime import datetime
import time
import pika
from pika import credentials
from pika.exceptions import AMQPConnectionError, AMQPChannelError

from pytest_zafira.exceptions import APIError
from pytest_zafira.api import zafira_client
from pytest_zafira import ZafiraListener
from pytest_zafira.utils import Context
from pytest_zafira.constants import PARAMETER


class RabbitHandler(logging.Handler):
    """
    handler that send log to rabbitmq, using pika.
    """
    logger = logging.getLogger('zafira')

    def __init__(self):
        logging.Handler.__init__(self)
        self.zafira_connected = self.__connect_to_zafira()
        self.password = 'qpsdemo'
        self.exchange = 'logs'
        self.connection = None
        self.channel = None
        self.virtual_host = '/'
        self.type = 'x-recent-history'
        self.history = 1000
        self.routing_key = ''
        # make sure exchange only declared once.
        self.is_exchange_declared = False
        # lock for serializing log sending, because pika is not thread safe.
        self.emit_lock = threading.Lock()
        # init connection.
        self.connection_params = dict(
            host=self.host,
            port=self.port,
            virtual_host=self.virtual_host,
            credentials=credentials.PlainCredentials(self.username,
                                                     self.password)
        )
        self.activate_options()

    def activate_options(self):
        """
        connect to rabbitMq server, using logs exchange
        """
        moment = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.routing_key = ZafiraListener().get_ci_run_id()
        self.connection_params['heartbeat_interval'] = 10
        if self.zafira_connected:
            try:
                self.__create_connection()
            except AMQPConnectionError:
                self.logger.error('{} - [mq] Connect fail.'.format(moment))
                return
            self.logger.info('{} - [mq] Connect success.'.format(moment))
            try:
                self.__create_channel()
            except AMQPChannelError:
                self.logger.error(
                    '{} - [mq] Unable to open channel.'.format(moment)
                )
                return
            try:
                self.__create_exchange()
            except AMQPChannelError:
                self.logger.error(
                    '{} - [mq] Unable to declare exchange.'.format(moment)
                )
                return
            self.logger.info(
                    '{} - [mq] Declare exchange success.'.format(moment)
            )

    def emit(self, record):
        """
        publish message to RabitMQ consumer
        :param record: LogRecord object
        :return:
        """
        test_id = ZafiraListener().ci_test_id
        if test_id:
            correlation_id = '{}_{}'.format(self.routing_key, test_id)
        else:
            correlation_id = ''.join(self.routing_key)
        self.emit_lock.acquire()
        try:
            if not self.connection or not self.channel:
                self.activate_options()
            self.channel.basic_publish(exchange=self.exchange,
                                       routing_key=self.routing_key,
                                       body=LogstashFormatter().format(record),
                                       properties=pika.BasicProperties(
                                           delivery_mode=1,
                                           correlation_id=correlation_id,
                                           content_type='application/json'
                                       ))
        except Exception:
            # for the sake of reconnect
            self.channel = None
            self.connection = None
            self.handleError(record)
        finally:
            self.emit_lock.release()

    def __create_connection(self):
        if not self.connection or not self.connection.is_open:
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    **self.connection_params
                )
            )
        return self.connection

    def __create_channel(self):
        if not self.channel or\
                not self.channel.is_open and\
                self.connection and\
                self.connection.is_open:
            self.channel = self.connection.channel(1)
        return self.channel

    def __create_exchange(self):
        if self.channel and self.channel.is_open:
            if not self.is_exchange_declared:
                args = {self.type: self.history}
                self.channel.exchange_declare(exchange=self.exchange,
                                              type=self.type,
                                              durable=False,
                                              auto_delete=False,
                                              arguments=args)
                self.is_exchange_declared = True

    def __connect_to_zafira(self):
        connected = False
        try:
            if Context.get(PARAMETER['ZAFIRA_ENABLED']) == 'True':
                resp = zafira_client.get_setting_tool('RABBITMQ', True)
                if resp.status_code == 200:
                    settings = resp.json()
                    if settings:
                        for setting in settings:
                            if 'RABBITMQ_HOST' in setting['name']:
                                self.host = setting['value']
                            elif 'RABBITMQ_PORT' in setting['name']:
                                self.port = int(setting['value'])
                            elif 'RABBITMQ_USER' in setting['name']:
                                self.username = setting['value']
                            elif 'RABBITMQ_ENABLED' in setting['name']:
                                connected = bool(setting['value'])
        except APIError:
            logging.error(
                '{} - [mq] Unable to connect with Zafira.'.format(
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )
            )
        return connected

    def close(self):
        """
        clear when closing
        """
        self.acquire()
        moment = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            if self.channel and self.channel.is_open:
                try:
                    self.channel.close()
                except (IOError, TimeoutError):
                    self.logger.error(
                        '{} - [mq] Unable to close channel.'.format(moment)
                    )
            if self.connection and self.connection.is_open:
                try:
                    self.connection.close()
                except IOError:
                    self.logger.error(
                        '{} - [mq] Unable to close connection.'.format(moment)
                    )
                    self.logger.error(
                        '{} - [mq] Cleanup success.'.format(moment)
                    )
        finally:
            self.release()


class LogstashFormatter(logging.Formatter):
    """
    Custom logging JSON formatter, contains methods to format log record in
    logstash-compatible format
    """

    @classmethod
    def serialize(cls, message):
        return bytes(json.dumps(message), 'utf-8')

    def format(self, record):
        """
        Formats log record into logstash-compatible format
        :return: JSON representation of log record
        """
        message = {}
        self.write_basic(message, record)
        if Context.get(PARAMETER['S3_SAVE_SCREENSHOTS']) and\
                'META_INFO' == record.levelname:
            self.write_with_headers(message, record)

        json_obj = bytes(json.dumps(message), 'utf-8')
        return json_obj

    def write_basic(self, message, record):
        basic_log = {
            'timestamp': time.time() * 1000,
            'threadName': normalized_thread_name(record.threadName),
            'logger': record.name,
            'message': record.msg,
            'level': record.levelname
        }
        message.update(basic_log)

    def write_with_headers(self, message, record):
        headers = {
            'headers': {
                'AMAZON_PATH': record.amazon_path,
                'CI_TEST_ID': record.test_id,
                'AMAZON_PATH_CORRELATION_ID': record.correlation_id
            }
        }
        message.update(headers)


def normalized_thread_name(thread_name):
    """
    Simplifies a long names of thread (for Zafira UI),
    e.g. MainThread -> MT, ThreadPoolExecutor -> TPE, etc.
    :param thread_name: thread name from Log Record object
    :return: simplified thread name
    """
    normalized = ''
    for symb in thread_name:
        if symb.isupper():
            normalized += symb
    return normalized
