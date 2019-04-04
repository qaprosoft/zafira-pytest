from pytest_zafira.constants import (TEST_STATUS,
                                     INITIATOR,
                                     DRIVER_MODE,
                                     URL_PATH,
                                     PARAMETER)

from pytest_zafira.utils.context import Context

from .api_request import APIRequest
from .payloads import (job,
                       refresh_token,
                       test,
                       test_suite,
                       test_case,
                       test_run,
                       test_artifact)


class ZafiraClient:
    DEFAULT_USER = "anonymous"

    def __init__(self):
        self.access_token = ''
        self.api = APIRequest(Context.get(PARAMETER['SERVICE_URL']))

    def get_setting_tool(self, tool, decrypt):
        return self.api.get(
            URL_PATH['GET_SETTING_TOOL_PATH'].format(tool, decrypt),
            self.init_auth_headers(),
            "Unable to get settings by tool"
        )

    def is_zafira_available(self):
        status_code = self.api.get(
            URL_PATH['STATUS_PATH'],
            default_err_msg="Unable to send ping"
        ).status_code
        return status_code == 200

    def create_test_suite(self,
                          user_id,
                          suite_name,
                          file_name,
                          description=None):

        test_suite['userId'] = user_id
        test_suite['description'] = description
        test_suite['fileName'] = file_name
        test_suite['name'] = suite_name

        return self.api.post(
            URL_PATH['TEST_SUITES_PATH'],
            test_suite,
            self.init_auth_headers(),
            "Unable to create test suite"
        )

    def create_test_case(self,
                         test_class,
                         test_method,
                         test_suite_id,
                         user_id,
                         info=None,
                         project=None):

        test_case['testClass'] = test_class
        test_case['testMethod'] = test_method
        test_case['testSuiteId'] = test_suite_id
        test_case['primaryOwnerId'] = user_id
        test_case['info'] = info
        test_case['project'] = project

        return self.api.post(
            URL_PATH['TEST_CASES_PATH'],
            test_case,
            self.init_auth_headers(),
            "Unable to create test case"
        )

    def create_job(self, user_id, job_name, job_url, jenkins_host):
        job["userId"] = user_id
        job["jobURL"] = job_url
        job["name"] = job_name
        job["jenkinsHost"] = jenkins_host

        return self.api.post(
            URL_PATH['JOBS_PATH'],
            job,
            self.init_auth_headers(),
            "Unable to create job"
        )

    def start_test_run(self,
                       job_id,
                       test_suite_id,
                       build_number,
                       started_by=INITIATOR['SCHEDULER'],
                       driver_mode=DRIVER_MODE['METHOD_MODE'],
                       config=None,
                       blocker=None,
                       work_item=None,
                       status=None,
                       project=None,
                       known_issue=None):

        test_run["jobId"] = job_id
        test_run["testSuiteId"] = test_suite_id
        test_run["buildNumber"] = build_number
        test_run["startedBy"] = started_by
        test_run["driverMode"] = driver_mode
        test_run["blocker"] = blocker
        test_run["workItem"] = work_item
        test_run["status"] = status
        test_run["project"] = project
        test_run["knownIssue"] = known_issue
        test_run["configXML"] = config

        return self.api.post(
            URL_PATH['TEST_RUNS_PATH'],
            test_run,
            self.init_auth_headers(),
            "Unable to start test run"
        )

    def finish_test_run(self, test_run_id):
        return self.api.post(
            URL_PATH['TEST_RUNS_FINISH_PATH'].format(test_run_id),
            headers=self.init_auth_headers(),
            default_err_msg="Unable to finish test run"
        )

    def start_test(self,
                   test_run_id,
                   test_case_id,
                   test_name,
                   start_time,
                   ci_test_id,
                   status=TEST_STATUS['IN_PROGRESS'],
                   test_class=None,
                   test_group=None,
                   work_items=None):

        test["testRunId"] = test_run_id
        test["testCaseId"] = test_case_id
        test["name"] = test_name
        test["ciTestId"] = ci_test_id
        test["startTime"] = start_time
        test["testClass"] = test_class
        test["status"] = status
        test["workItems"] = work_items
        test["testGroup"] = test_group

        return self.api.post(
            URL_PATH['TESTS_PATH'],
            test,
            self.init_auth_headers(),
            "Unable to start test"
        )

    def finish_test(self, test):
        return self.api.post(
            URL_PATH['TEST_FINISH_PATH'].format(test["id"]),
            test,
            self.init_auth_headers(),
            "Unable to finish test"
        )

    def add_test_artifact_to_test(self,
                                  test_id,
                                  artifact_name,
                                  link='',
                                  expires_in=None):

        test_artifact["testId"] = test_id
        test_artifact["link"] = link
        test_artifact["name"] = artifact_name
        if expires_in is None:
            expires_in = Context.get(
                        PARAMETER['ARTIFACT_EXPIRES_IN_DEFAULT_TIME']
                    )

        test_artifact["expiresIn"] = expires_in

        return self.api.post(
            URL_PATH['ADD_TEST_ARTIFACT'].format(test_id),
            test_artifact,
            self.init_auth_headers(),
            "Unable to add test artifact"
        )

    def refresh_token(self, token):
        refresh_token["refreshToken"] = token

        return self.api.post_without_authorization(
            URL_PATH['REFRESH_TOKEN_PATH'],
            refresh_token,
            "Unable to refresh token"
        )

    def create_test_work_items(self, test_id, list_work_items):
        return self.api.post(
            URL_PATH['TEST_WORK_ITEMS_PATH'].format(test_id),
            list_work_items,
            self.init_auth_headers(),
            "Unable to create workitems"
        )

    def get_user_profile(self, username=None):
        url = URL_PATH['PROFILE_PATH']
        url = url + "?username=" + username if username else url

        return self.api.get(
            url,
            self.init_auth_headers(),
            "Unable to authorize user"
        )

    def init_auth_headers(self):
        return {"Authorization": "Bearer " + self.access_token}


zafira_client = ZafiraClient()
