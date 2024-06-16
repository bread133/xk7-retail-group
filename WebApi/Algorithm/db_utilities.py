import psycopg2
from configparser import ConfigParser


def load_config(filename='database.ini', section='postgresql') -> dict[str]:
    """
    Performs loading of the config file

    :param filename: path to configuration file
    :param section: section name in configuration file
    :return: dictionary with found parameters
    """
    parser = ConfigParser()
    parser.read(filename)

    config = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            config[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return config

