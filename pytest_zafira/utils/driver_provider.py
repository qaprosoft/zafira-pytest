from concurrent import futures
from concurrent.futures import Future

from pytest_zafira.exceptions import DriverError


class BaseDriverProvider:
    def get_drivers(self):
        """ An abstract method which provides an instances of drivers """


class MyDriverProvider(BaseDriverProvider):
    """
    My-specific class, provides get-drivers functionality (for customer,
    agent, admin-agent and admin)
    """
    def __init__(self, driver_pool):
        self.num_of_drivers = len(driver_pool)
        self.thread_pool = futures.ThreadPoolExecutor(
            max_workers=self.num_of_drivers
        )

        self.driver_pool = driver_pool

    def get_drivers(self):
        drivers = []
        for driver in self.driver_pool:
            # gets single driver and submits it to the future
            future = self.thread_pool.submit(lambda: driver.driver)
            self.__exit_on_exception(future)
            drivers.append(self.__extract_driver(future))

        return drivers

    @staticmethod
    def __extract_driver(driver_or_future):
        if isinstance(driver_or_future, Future):
            return driver_or_future.result()
        else:
            return driver_or_future

    @staticmethod
    def __exit_on_exception(future):
        finished_set = futures.wait([future],
                                    return_when=futures.FIRST_EXCEPTION)
        finished_future = list(finished_set.done)[0]
        if finished_future.exception():
            err_msg = "EXCEPTION THROWN BY THREAD DURING GET_DRIVERS {} !!!"\
                .format(finished_future.exception())

            raise DriverError(err_msg)
