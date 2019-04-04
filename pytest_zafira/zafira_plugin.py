import time
import logging
import pytest
import uuid

from .constants import PARAMETER, TEST_STATUS, CONFIG

from .api import zafira_client
from .utils import Context
from .exceptions import ZafiraError


class PyTestZafiraPlugin:
    """
    Contains hook implementations and helper methods
    """
    ZAFIRA_ENABLED = False
    ZAFIRA_URL = None
    ZAFIRA_ACCESS_TOKEN = None
    user = None
    job = None
    test_suite = None
    refresh_token = None
    test_case = None
    test_run = None
    test = None
    zc = None
    ci_test_id = None

    __INSTANCE = None

    skip_reason = None
    MAX_LENGTH_OF_WORKITEM = 46

    logger = logging.getLogger('zafira')

    def __new__(cls):
        if not cls.__INSTANCE:
            cls.__INSTANCE = super(PyTestZafiraPlugin, cls).__new__(cls)
        return cls.__INSTANCE

    @pytest.hookimpl
    def pytest_sessionstart(self, session):
        """
        Setup-class handler, signs in user, creates a testsuite,
        testcase, job and registers testrun in Zafira
        """
        initialized = self.__initialize_zafira()
        if not initialized:
            return
        try:
            job_name = Context.get(PARAMETER['JOB_NAME'])
            suite_name = Context.get(PARAMETER['SUITE_NAME'])
            self.user = self.zc.get_user_profile().json()

            self.test_suite = self.zc.create_test_suite(
                self.user["id"],
                suite_name,
                'filename'
            ).json()

            self.job = self.zc.create_job(
                self.user["id"],
                job_name,
                str(time.time()),
                "jenkins_host"
            ).json()

            self.test_run = self.zc.start_test_run(
                self.job["id"],
                self.test_suite["id"],
                0,
                config=CONFIG
            ).json()

        except ZafiraError as e:
            self.ZAFIRA_ENABLED = False
            self.logger.error(
                "Undefined error during test run registration!",
                e
            )

    @pytest.hookimpl
    def pytest_runtest_setup(self, item):
        """
        Setup handler, set up initial parameters for test,
        attaches to testsuite, registers and starts the test
        """
        if not self.ZAFIRA_ENABLED:
            return
        try:
            test_name = item.name
            class_name = item.nodeid.split('::')[1]
            self.ci_test_id = str(uuid.uuid4())

            package = ''
            self.test_case = self.zc.create_test_case(
                class_name,
                test_name,
                self.test_suite["id"],
                self.user["id"]
            ).json()

            work_items = []

            if hasattr(item._evalxfail, 'reason'):
                work_items.append('xfail')

            self.test = self.zc.start_test(
                self.test_run["id"],
                self.test_case["id"],
                test_name,
                round(time.time() * 1000),
                self.ci_test_id,
                TEST_STATUS['IN_PROGRESS'],
                class_name,
                package,
                work_items
            ).json()

        except ZafiraError as e:
            self.logger.error(
                "Undefined error during test case/method start!",
                e
            )

    @pytest.hookimpl
    def pytest_runtest_teardown(self, item):
        """
        Teardown handler. Finishes test, adds workitems if needed
        """
        if not self.ZAFIRA_ENABLED:
            return
        try:
            if item._skipped_by_mark:
                test_name = item.name
                class_name = item.nodeid.split('::')[1]
                full_path_to_file = item.nodeid.split('::')[0].split('/')
                package = self.compose_package_name(full_path_to_file) + '/'
                self.test_case = self.zc.create_test_case(
                    class_name,
                    test_name,
                    self.test_suite["id"],
                    self.user["id"]
                ).json()

                self.test = self.zc.start_test(
                    self.test_run["id"],
                    self.test_case["id"],
                    test_name,
                    round(time.time() * 1000),
                    self.ci_test_id,
                    test_class=class_name,
                    test_group=package
                ).json()

                self.test['status'] = TEST_STATUS['SKIPPED']
                self.add_work_item_to_test(self.test['id'], self.skip_reason)

            self.zc.finish_test(self.test)
        except ZafiraError as e:
            self.logger.error("Unable to finish test run correctly", e)

    @pytest.hookimpl
    def pytest_runtest_logreport(self, report):
        """
        Set test status, stacktrace if needed
        :param report: info about test
        """
        if not self.ZAFIRA_ENABLED:
            return
        try:
            if report.when == 'setup':
                if report.skipped:
                    self.skip_reason = report.longrepr[2]
                if report.failed:
                    self.on_test_failure(self.test, report)
            if report.when == 'call':
                self.test["finishTime"] = round(time.time() * 1000)
                test_result = report.outcome
                if test_result == 'passed':
                    self.on_test_success(self.test)
                elif test_result == 'failed':
                    self.on_test_failure(self.test, report)
                else:
                    self.on_test_skipped(self.test, report)
                self.add_artifact_to_test(
                    self.test,
                    Context.get(PARAMETER['ARTIFACT_LOG_NAME']),
                )
        except ZafiraError as e:
            self.logger.error("Unable to finish test correctly", e)

    @pytest.hookimpl
    def pytest_sessionfinish(self, session, exitstatus):
        """
        Teardown-class handler, closes the testrun
        """
        if not self.ZAFIRA_ENABLED:
            return

        try:
            self.zc.finish_test_run(self.test_run["id"])
        except ZafiraError as e:
            self.logger.error("Unable to finish test run correctly", e)

    def compose_package_name(self, path_entries_list):
        return '/'.join(path_entries_list)

    def add_artifact_to_test(self,
                             test,
                             artifact_name,
                             artifact_link='',
                             expires_in=None):
        """
        Adds test artifact to test
        """
        try:
            self.zc.add_test_artifact_to_test(
                test["id"],
                artifact_link,
                artifact_name,
                expires_in
            )
        except ZafiraError as e:
            self.logger.error("Unable to add artifact to test correctly", e)

    def __initialize_zafira(self):
        enabled = False
        try:
            ZAFIRA_ENABLED = Context.get(PARAMETER['ZAFIRA_ENABLED'])
            self.ZAFIRA_ENABLED = ZAFIRA_ENABLED == 'True'
            self.ZAFIRA_ACCESS_TOKEN = Context.get(PARAMETER['ACCESS_TOKEN'])

            if self.ZAFIRA_ENABLED:

                self.zc = zafira_client
                self.ZAFIRA_ENABLED = self.zc.is_zafira_available()

                if self.ZAFIRA_ENABLED:
                    self.refresh_token = self.zc.refresh_token(
                        self.ZAFIRA_ACCESS_TOKEN
                    ).json()
                    self.zc.access_token = self.refresh_token['accessToken']
                    if self.ZAFIRA_ENABLED:
                        is_available = "available"
                    else:
                        is_available = "unavailable"
                    self.logger.info("Zafira is " + is_available)

            enabled = self.ZAFIRA_ENABLED
        except ZafiraError as e:
            self.logger.error("Unable to find config property: ", e)
        return enabled

    @staticmethod
    def on_test_success(test):
        test['status'] = TEST_STATUS['PASSED']

    @staticmethod
    def on_test_failure(test, report):
        test['status'] = TEST_STATUS['FAILED']
        test['message'] = report.longreprtext

    @staticmethod
    def on_test_skipped(test, report):
        test['message'] = report.longreprtext
        if not hasattr(report, 'wasxfail'):
            test['status'] = TEST_STATUS['SKIPPED']
        else:
            test['status'] = TEST_STATUS['FAILED']

    def get_ci_run_id(self):
        return self.test_run['ciRunId']

    def add_work_item_to_test(self, test_id, work_item):
        if not self.ZAFIRA_ENABLED:
            return
        try:
            work_items = list()
            lenght_check = len(work_item) < self.MAX_LENGTH_OF_WORKITEM
            work_items.append(work_item if lenght_check else 'Skipped')
            self.zc.create_test_work_items(test_id, work_items)
        except ZafiraError as e:
            self.logger.error("Unable to add work item: ", e)


def pytest_configure(config):
    """
    Attaches wrapped hooks as plugin
    """
    config.pluginmanager.register(PyTestZafiraPlugin())
