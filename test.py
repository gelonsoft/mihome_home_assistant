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
#response = api.connector.execute_mi_api("/miotspec/prop/get", 'cn',
#                                         {"data": '{"params":[{"did":"blt.3.1153a9j40ls00","siid":2,"piid":1},{"did":"blt.3.1153a9j40ls00","siid":2,"piid":2}],"datasource":1}'})
#print(response)
response = api.connector.execute_mi_api("/miotspec/prop/get", 'cn',
                                         {"data": '{"params":[{"did":"13388725","siid":3,"piid":1},{"did":"blt.3.1153a9j40ls00","siid":1,"piid":1}],"datasource":1}'})
print(response)
#print(api.get_device_desc_from_cloud())
#for device_type, devices in api.ha_devices.items():
#    print(devices)
    #setup_platform(hass, None, None, 'gelonsoftmihome', devices, )

#print(api.connector.get_device_spec("zhimi.airpurifier.m1"))
#z={'type': 'urn:miot-spec-v2:device:air-purifier:0000A007:zhimi-m1:1', 'description': 'Air Purifier', 'services': [{'iid': 1, 'type': 'urn:miot-spec-v2:service:device-information:00007801:zhimi-m1:1', 'description': 'Device Information', 'properties': [{'iid': 1, 'type': 'urn:miot-spec-v2:property:manufacturer:00000001:zhimi-m1:1', 'description': 'Device Manufacturer', 'format': 'string', 'access': ['read']}, {'iid': 2, 'type': 'urn:miot-spec-v2:property:model:00000002:zhimi-m1:1', 'description': 'Device Model', 'format': 'string', 'access': ['read']}, {'iid': 3, 'type': 'urn:miot-spec-v2:property:serial-number:00000003:zhimi-m1:1', 'description': 'Device Serial Number', 'format': 'string', 'access': ['read']}, {'iid': 4, 'type': 'urn:miot-spec-v2:property:name:00000004:zhimi-m1:1', 'description': 'Device Name', 'format': 'string', 'access': ['read']}, {'iid': 5, 'type': 'urn:miot-spec-v2:property:firmware-revision:00000005:zhimi-m1:1', 'description': 'Current Firmware Version', 'format': 'string', 'access': ['read']}]}, {'iid': 2, 'type': 'urn:miot-spec-v2:service:air-purifier:00007811:zhimi-m1:1', 'description': 'Air Purifier', 'properties': [{'iid': 1, 'type': 'urn:miot-spec-v2:property:on:00000006:zhimi-m1:1', 'description': 'Switch Status', 'format': 'bool', 'access': ['read', 'write', 'notify']}, {'iid': 2, 'type': 'urn:miot-spec-v2:property:fan-level:00000016:zhimi-m1:1', 'description': 'Fan Level', 'format': 'uint8', 'access': ['read', 'write', 'notify'], 'value-list': [{'value': 0, 'description': 'Auto'}, {'value': 1, 'description': 'Sleep'}, {'value': 2, 'description': 'Favorite'}]}, {'iid': 3, 'type': 'urn:miot-spec-v2:property:mode:00000008:zhimi-m1:1', 'description': 'Mode', 'format': 'uint8', 'access': ['read', 'write'], 'value-list': [{'value': 0, 'description': 'Auto'}, {'value': 1, 'description': 'Sleep'}, {'value': 2, 'description': 'Favorite'}]}]}, {'iid': 3, 'type': 'urn:miot-spec-v2:service:environment:0000780A:zhimi-m1:1', 'description': 'Environment', 'properties': [{'iid': 1, 'type': 'urn:miot-spec-v2:property:relative-humidity:0000000C:zhimi-m1:1', 'description': 'Relative Humidity', 'format': 'uint8', 'access': ['read', 'notify'], 'unit': 'percentage', 'value-range': [0, 100, 1]}, {'iid': 2, 'type': 'urn:miot-spec-v2:property:pm2.5-density:00000034:zhimi-m1:1', 'description': 'PM2.5 Density', 'format': 'float', 'access': ['read', 'notify'], 'value-range': [0, 600, 1]}, {'iid': 3, 'type': 'urn:miot-spec-v2:property:temperature:00000020:zhimi-m1:1', 'description': 'Indoor Temperature', 'format': 'float', 'access': ['read', 'notify'], 'unit': 'celsius', 'value-range': [-40, 125, 0.1]}]}, {'iid': 4, 'type': 'urn:miot-spec-v2:service:filter:0000780B:zhimi-m1:1', 'description': 'Filter', 'properties': [{'iid': 1, 'type': 'urn:miot-spec-v2:property:filter-life-level:0000001E:zhimi-m1:1', 'description': 'Filter Life Level', 'format': 'uint8', 'access': ['read', 'notify'], 'unit': 'percentage', 'value-range': [0, 100, 1]}, {'iid': 2, 'type': 'urn:miot-spec-v2:property:filter-used-time:00000048:zhimi-m1:1', 'description': 'Filter Used Time', 'format': 'uint16', 'access': ['read', 'notify'], 'unit': 'hours', 'value-range': [0, 10000, 1]}]}, {'iid': 5, 'type': 'urn:miot-spec-v2:service:indicator-light:00007803:zhimi-m1:1', 'description': 'Indicator Light', 'properties': [{'iid': 1, 'type': 'urn:miot-spec-v2:property:on:00000006:zhimi-m1:1', 'description': 'Switch Status', 'format': 'bool', 'access': ['read', 'write', 'notify']}]}, {'iid': 6, 'type': 'urn:miot-spec-v2:service:alarm:00007804:zhimi-m1:1', 'description': 'Alarm', 'properties': [{'iid': 1, 'type': 'urn:miot-spec-v2:property:alarm:00000012:zhimi-m1:1', 'description': 'Alarm', 'format': 'bool', 'access': ['read', 'write', 'notify']}]}, {'iid': 7, 'type': 'urn:miot-spec-v2:service:physical-controls-locked:00007807:zhimi-m1:1', 'description': 'Physical Control Locked', 'properties': [{'iid': 1, 'type': 'urn:miot-spec-v2:property:physical-controls-locked:0000001D:zhimi-m1:1', 'description': 'Physical Control Locked', 'format': 'bool', 'access': ['read', 'write', 'notify']}]}]}
print(api.connector.get_device_spec("zhimi.airpurifier.m1"))
print(api.connector.get_device_spec("zhimi.airpurifier.m1"))

