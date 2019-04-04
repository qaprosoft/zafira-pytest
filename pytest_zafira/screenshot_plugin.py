import pytest
import logging
import itertools
from concurrent.futures import ProcessPoolExecutor

from pytest_zafira.utils import MyDriverProvider
from pytest_zafira.utils.screenshot import Screenshot
from pytest_zafira.services import amazon_cloud_service


class ZafiraScreenshotCapture:

    amazon_connector = amazon_cloud_service
    driver_provider = None
    logger = logging.getLogger('zafira')

    @pytest.hookimpl
    def pytest_runtest_makereport(self, item, call):
        """
        Catches a screenshot as bytearray and saves it into s3 bucket when an
        exception occurs
        :param item: info about running test and its instance of and
                     instanceof params
        :param call: info about call
        :return:
        """
        with ProcessPoolExecutor() as executor:
            if not self.on_exception(item, call):
                return

            self.logger.debug('Exception occurs... '
                              'Trying to catch screenshot')

            if hasattr(item.instance, 'driver'):
                executor.submit(
                    Screenshot.upload_to_amazon_S3,
                    bytes(
                        item.instance.driver.get_screenshot_as_base64(),
                        'utf-8'
                    )
                )
            elif hasattr(item.instance, 'drivers'):
                failed_drivers = self.get_failed_drivers(
                    list(item.instance.drivers.values()),
                    call
                )

                drivers = MyDriverProvider(failed_drivers).get_drivers()

                for driver in drivers:
                    executor.submit(
                        Screenshot.upload_to_amazon_S3,
                        bytes(driver.get_screenshot_as_base64(), 'utf-8')
                    )

    @staticmethod
    def on_exception(item, call):
        return hasattr(item.instance, 'driver' or 'drivers') and call.excinfo

    @staticmethod
    def get_failed_drivers(drivers, call):
        """
        Filters failed driver objects where exception occurs
        :param drivers: list of drivers assigned to test item
        :param call: interpeter info about exception
        :return: list of failed drivers. In case if call doesn't
        contain any info about exception, method will return full
        list of drivers
        """
        failed_drivers = [
            driver[0] for driver in drivers
            if driver[0].__str__() in call.__str__()
        ]

        if len(failed_drivers):
            return failed_drivers
        else:
            return list(itertools.chain.from_iterable(drivers))


def pytest_configure(config):
    """
    Attaches wrapped hooks as plugin
    """
    config.pluginmanager.register(ZafiraScreenshotCapture())
