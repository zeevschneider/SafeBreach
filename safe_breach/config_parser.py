import yaml
from collections import namedtuple

conf_file = '../config/email_server.yml'


def get_config_data(config_file=conf_file):
    """
        Get configuration
    :param config_file: config file
    :return: config data
    """
    Connection = namedtuple("Connection", "server_config domain_config")

    with open(config_file, "r") as f:
        config = yaml.safe_load(f)
        server_conf = config["Connectivity"]
        domain_config = config["Domain"]

    return Connection(server_conf, domain_config)

