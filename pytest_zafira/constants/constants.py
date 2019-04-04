URL_PATH = {
    'STATUS_PATH': '/api/status',
    'REFRESH_TOKEN_PATH': '/api/auth/refresh',
    'LOGIN_PATH': '/api/auth/login',
    'PROFILE_PATH': '/api/users/profile',
    'TEST_SUITES_PATH': '/api/tests/suites',
    'TEST_CASES_PATH': '/api/tests/cases',
    'JOBS_PATH': '/api/jobs',
    'TEST_RUNS_PATH': '/api/tests/runs',
    'TESTS_PATH': '/api/tests',
    'TEST_FINISH_PATH': '/api/tests/{}/finish',
    'TEST_RUNS_FINISH_PATH': '/api/tests/runs/{}/finish',
    'TEST_RUNS_ABORT_PATH': '/api/tests/runs/abort?id={}',
    'TEST_BY_ID_PATH': '/api/tests/{}',
    'ADD_TEST_ARTIFACT': '/api/tests/{}/artifacts',
    'TEST_WORK_ITEMS_PATH': '/api/tests/{}/workitems',
    'TEST_RUNS_RESULTS_PATH': '/api/tests/runs/{}/results',
    'USERS_PATH': '/api/users',
    'PROJECT_PATH': '/api/projects',
    'GET_SETTING_TOOL_PATH': '/api/settings/tool/{}?decrypt={}'
}


TEST_STATUS = {'UNKNOWN': 'UNKNOWN',
               'IN_PROGRESS': 'IN_PROGRESS',
               'PASSED': 'PASSED',
               'FAILED': 'FAILED',
               'SKIPPED': 'SKIPPED',
               'ABORTED': 'ABORTED',
               'QUEUED': 'QUEUED'}


INITIATOR = {'SCHEDULER': 'SCHEDULER',
             'UPSTREAM_JOB': 'UPSTREAM_JOB',
             'HUMAN': 'HUMAN'}


DRIVER_MODE = {'METHOD_MODE': 'METHOD_MODE',
               'CLASS_MODE': 'CLASS_MODE',
               'SUITE_MODE': 'SUITE_MODE'}


PARAMETER = {
    'BASE_URL': 'base_url',
    'SERVICE_URL': 'service-url',
    'ACCESS_TOKEN': 'access_token',
    'ZAFIRA_ENABLED': 'zafira_enabled',
    'JOB_NAME': 'job_name',
    'SUITE_NAME': 'suite_name',
    'ARTIFACT_EXPIRES_IN_DEFAULT_TIME': 'artifact_expires_in_default_time',
    'ARTIFACT_LOG_NAME': 'artifact_log_name',
    'AWS_ACCESS_KEY': 'aws_access_key',
    'AWS_SECRET_KEY': 'aws_secret_key',
    'AWS_SCREEN_SHOT_BUCKET': 'aws_screen_shot_bucket',
    'S3_SAVE_SCREENSHOTS': 's3_save_screenshots'
}


CONFIG = "<config><arg unique='false'><key>platform</key><value>" + \
         "CHROME" + \
         "</value></arg><arg unique='false'><key>env</key><value>" + \
         "DEMO" + \
         "</value></arg></config>"
