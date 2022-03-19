import yaml

conf_file = '../config/email_server.yml'


def get_config_data(config_file=conf_file):

    with open(config_file, "r") as f:
        config = yaml.safe_load(f)
        server_conf = config["Connectivity"]

    return server_conf

