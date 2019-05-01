=============
pytest-zafira
=============

.. image:: https://img.shields.io/pypi/v/pytest-zafira.svg
    :target: https://pypi.org/project/pytest-zafira
    :alt: PyPI version

.. image:: https://img.shields.io/pypi/pyversions/pytest-zafira.svg
    :target: https://pypi.org/project/pytest-zafira
    :alt: Python versions

Zafira plugin for pytest
__________________________

Pytest plugin for integration with `Zafira`_.

----


Installation
------------

Install using command::

    $ pip install pytest-zafira

Enable the fixture explicitly in your tests or conftest.py::

    pytest_plugins = ['pytest_zafira.zafira_plugin', 'pytest_zafira.screenshot_plugin']


Configuration
-------------

pytest-zafira plugin searches configuration file in the current working directory and it called 'zafira_properties.ini'. File has to look like::

     [config]
     service-url = url for zafira-server + '/zafira-ws'
     zafira_enabled = True (turn on/off fixture)
     zafira_app_url = url of deployed zafira
     access_token = access_token from Zafira dashboard
     job_name = any string you like
     suite_name = any string you like
     artifact_expires_in_default_time = (int value in sec.) an expiration time for amazon bucket link
     artifact_log_name = test_logs
     aws_access_key = secret
     aws_secret_key = secret
     aws_screen_shot_bucket = secret
     s3_save_screenshots = True (save screenshots to AWS S3 bucket)

More about access_token find here `Integration of Zafira`_.

After that step you have to configure logging. An example of logging configuration file (yaml)::

    version: 1
    formatters:
      default_formatter:
        format: '%(asctime)s:%(levelname)s - %(message)s'
        datefmt: '%H:%M:%S'
    handlers:
      console:
        class: logging.StreamHandler
        level: 0
        formatter: default_formatter
        stream: ext://sys.stdout
      zafira_log_appender:
        class: pytest_zafira.RabbitHandler
    loggers:
      zafira:
        level: INFO
        handlers: [console, zafira_log_appender]
        propagate: no
    root:
      level: WARN
      handlers: [console, zafira_log_appender]

Then add META_INFO logging level for logger::

    import logging.config
    import os

    import yaml


    class LoggingConfiguration:
        def __init__(self):
            self.ROOT_LOG_LEVEL = self.fetch_env(expected_env='ROOT_LOG_LEVEL', default='')

            self.ZAFIRA_LOG_LEVEL = self.fetch_env(expected_env='ZAFIRA_LOG_LEVEL', default='')

            # and this level is responsible for screenshots
            self.add_meta_info_level()
            # apply configuration from logging.cfg
            self.apply_configuration()
            # set log level according to env variables, do nothing if they empty or overwrite default from logging.cfg
            self.init_loggers()

        def init_loggers(self):
            zafira_logger = logging.getLogger('zafira')
            if self.ZAFIRA_LOG_LEVEL:
                zafira_logger.setLevel(self.ZAFIRA_LOG_LEVEL)

        @staticmethod
        def add_meta_info_level():
            """
            Logging level for screenshots
            """
            meta_info_level = logging.DEBUG + 1
            add_logging_level('META_INFO', meta_info_level)

        def apply_configuration(self):
            config = yaml.load(open('path/to/your/logging/config/file.yml', 'r'))
            if self.ROOT_LOG_LEVEL:
                config['root']['level'] = os.environ['ROOT_LOG_LEVEL']
            logging.config.dictConfig(config)

        @staticmethod
        def fetch_env(expected_env, default):
            if expected_env in os.environ:
                return os.environ[expected_env]
            else:
                return default


    def add_logging_level(level_name, level_number):
        """
        Comprehensively adds a new logging level to the `logging` module and the
        currently configured logging class.

        `levelName` becomes an attribute of the `logging` module with the value
        `levelNum`. `methodName` becomes a convenience method for both `logging`
        itself and the class returned by `logging.getLoggerClass()` (usually just
        `logging.Logger`). If `methodName` is not specified, `levelName.lower()` is
        used.

        To avoid accidental clobberings of existing attributes, this method will
        raise an `AttributeError` if the level name is already an attribute of the
        `logging` module or if the method name is already present
        """
        method_name = level_name.lower()

        if hasattr(logging, level_name):
            raise AttributeError('{} already defined in logging module'.format(level_name))
        if hasattr(logging, method_name):
            raise AttributeError('{} already defined in logging module'.format(method_name))
        if hasattr(logging.getLoggerClass(), method_name):
            raise AttributeError('{} already defined in logger class'.format(method_name))

        def log_for_level(self, message, *args, **kwargs):
            if self.isEnabledFor(level_number):
                self._log(level_number, message, args, **kwargs)

        def log_to_root(message, *args, **kwargs):
            logging.log(level_number, message, *args, **kwargs)

        logging.addLevelName(level_number, level_name)
        setattr(logging, level_name, level_number)
        setattr(logging.getLoggerClass(), method_name, log_for_level)
        setattr(logging, method_name, log_to_root)

and activate this config when tests will start.

Usage
-----

To use just run the pytest`s tests.

License
-------

Distributed under the terms of the `Apache Software License 2.0`_ license, "pytest-zafira" is free and open source software


Issues
------

If you encounter any problems, please `file an issue`_ along with a detailed description.

.. _`Zafira`: https://github.com/qaprosoft/zafira
.. _`Integration of Zafira`: https://github.com/qaprosoft/zafira#integration
.. _`Apache Software License 2.0`: http://www.apache.org/licenses/LICENSE-2.0
.. _`file an issue`: https://github.com/qaprosoft/pytest-zafira/issues
.. _`Pytest`: https://docs.pytest.org/en/latest/writing_plugins.html#requiring-loading-plugins-in-a-test-module-or-conftest-file
.. _`pip`: https://pypi.org/project/pip/
.. _`PyPI`: https://pypi.org/proj
