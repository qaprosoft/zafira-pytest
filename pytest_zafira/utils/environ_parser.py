import logging
from os import environ

from pytest_zafira.exceptions import ConfigError


logger = logging.getLogger('settings')


def get_env_var(env_var_key):
    """
    Getter for environment variable keys.  Uses `os.environ.get(KEYNAME)`
    :param env_key:  Type string.  Key name of environment variable to get.
    :return:  Value of the environment variable.
    """
    env_var_value = environ.get(env_var_key)
    if env_var_value is None:
        logger.error('ENV var missing: [{}], please set this variable'.format(
                env_var_key
            )
        )
        raise ConfigError(
            "Env variable {} is mandatory, please set this variable".format(
                env_var_key
            )
        )
    else:
        logger.debug('ENV variable is: [{}]:[{}]'.format(env_var_key,
                                                         env_var_value))
    return env_var_value
