import logging
import requests
from pytest_zafira.exceptions import APIError


class APIRequest:
    """HTTP methods"""

    logger = logging.getLogger('zafira')

    def __init__(self, base_url):
        self.base_url = base_url

    def get(self,
            endpoint,
            headers=None,
            default_err_msg=None):

        url = self.base_url + endpoint
        try:
            response = requests.get(url=url, headers=headers)
        except APIError as e:
            self.logger.error(default_err_msg, e)
        return self.__verify_response(response, url, None)

    def post_without_authorization(self,
                                   endpoint,
                                   body=None,
                                   default_err_msg=None):

        url = self.base_url + endpoint
        try:
            response = requests.post(url, json=body)
        except APIError as e:
            self.logger.error(default_err_msg, e)
        return self.__verify_response(response, url, body)

    def post(self,
             endpoint,
             body=None,
             headers=None,
             default_err_msg=None):

        url = self.base_url + endpoint
        try:
            response = requests.post(url, json=body, headers=headers)
        except APIError as e:
            self.logger.error(default_err_msg, e)
        return self.__verify_response(response, url, body)

    @staticmethod
    def __verify_response(response, url=None, body=None):
        """
        Log and check API call. In case status code of response is not 200,
        will raise an HTTPException
        """
        status_code = response.status_code
        if status_code > 200:
            err_msg = "HTTP call fails." \
                      " Response status code {}" \
                      " from {}" \
                      " with body {}".format(status_code, url, body)

            raise APIError(err_msg)

        return response
