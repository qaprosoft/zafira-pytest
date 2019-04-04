class ZafiraError(Exception):
    """ Common exception for Zafira App """


class ConfigError(ZafiraError):
    """ Raises if environ var is missing """


class APIError(ZafiraError):
    """ An exception for Zafira client API calls issues """


class LoggingError(ZafiraError):
    """ Raises if issue in log appender occurs """


class DriverError(Exception):
    """ Raises when plugin cannot extract driver """
