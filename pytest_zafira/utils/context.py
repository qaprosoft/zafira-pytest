import configparser

CONFIG_FILE_PATH = '/Users/KhD/Desktop/PythonAT/zafira_properties.ini'


class Context:
    __CONFIG = None

    @classmethod
    def get(cls, parameter):
        if cls.__CONFIG is None:
            config = configparser.ConfigParser()
            config.read(CONFIG_FILE_PATH)
            cls.__CONFIG = config
        return cls.__CONFIG.get('config', parameter)
