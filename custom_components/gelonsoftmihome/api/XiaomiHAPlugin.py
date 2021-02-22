import logging
from custom_components.gelonsoftmihome.api.XiaomiCloudConnector import XiaomiCloudConnector
from custom_components.gelonsoftmihome.api.XiaomiDeviceFactory import XiaomiDeviceFactory
from custom_components.gelonsoftmihome.api.devices import AbstractMiDevice

servers = ["cn", "de", "us", "ru", "tw", "sg", "in", "i2"]


class XiaomiHAPlugin:
    def __init__(self, username: str, password: str, config_path: str):
        self.logger = logging.getLogger('gelonsoft.mihome.XiomiHAPlugin')
        self.username = username
        self.password = password
        self.config_path = config_path
        # a_yaml_file = open(self.config_path+self.name+"-one-credentials.yaml")
        #  yaml_config = yaml.load(a_yaml_file, Loader=yaml.FullLoader)
        # credentials = yaml_config.get("obmihome")
        self.connector = XiaomiCloudConnector("one", self.username, self.password, self.config_path)
        self.device_factory = XiaomiDeviceFactory(self.connector)
        self.internal_devices = []
        self.ha_devices = {}
        self.load_devices_from_cloud()

    def authorization(self):
        return self.connector.logged_in

    def get_device_desc_from_cloud(self):
        result = []
        for current_server in servers:
            response = self.connector.execute_mi_api("/home/device_list", current_server,
                                                     {"data": '{"getVirtualModel":false,"getHuamiDevices":0}'})
            if response is not None:
                for device in response["result"]["list"]:
                    device['country'] = current_server
                    result.append(device)
        return result

    def get_device_by_did(self, did) -> AbstractMiDevice:
        result = None
        for device in self.internal_devices:
            if device.did == did:
                result = device
                break
        return result

    def load_devices_from_cloud(self):
        if self.connector.logged_in:
            for device in self.get_device_desc_from_cloud():
                device_instance = self.device_factory.create_device_by_content(device)
                if device_instance:
                    self.internal_devices.append(device_instance)
                    ha_devs = device_instance.convert_to_ha_devices()
                    if ha_devs:
                        for ha_device_type, ha_devices in ha_devs.items():
                            if not self.ha_devices.get(ha_device_type):
                                self.ha_devices[ha_device_type] = []
                            for ha_device in ha_devices:
                                self.ha_devices[ha_device_type].append(ha_device)
        else:
            self.logger.error("XiaomiCloudConnector is not logged in")
