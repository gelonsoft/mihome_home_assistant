import yaml

from custom_components.gelonsoftmihome import XiaomiHAPlugin

a_yaml_file = open("data/one-credentials.yaml")
yaml_config = yaml.load(a_yaml_file, Loader=yaml.FullLoader)
credentials = yaml_config.get("obmihome")
api = XiaomiHAPlugin(credentials.get('username'),credentials.get('password'),'data/one')