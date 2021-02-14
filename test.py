import yaml

from custom_components.gelonsoftmihome import XiaomiHAPlugin
from custom_components.gelonsoftmihome.sensor import setup_platform

a_yaml_file = open("data/one-credentials.yaml")
yaml_config = yaml.load(a_yaml_file, Loader=yaml.FullLoader)
credentials = yaml_config.get("obmihome")
api = XiaomiHAPlugin(credentials.get('username'),credentials.get('password'),'data/one')

# setup_platform(hass, config, add_entities, discovery_info=None):
#hass=object
#hass.data={'gelonsoftmihome':api}
for device_type, devices in api.ha_devices.items():
    print(devices)
    #setup_platform(hass, None, None, 'gelonsoftmihome', devices, )