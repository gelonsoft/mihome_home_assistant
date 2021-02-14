import yaml
import logging
from gelonsoft.mihome.XiaomiCloudConnector import XiaomiCloudConnector
from gelonsoft.mihome.XiaomiDeviceFactory import XiaomiDeviceFactory

servers = ["cn", "de", "us", "ru", "tw", "sg", "in", "i2"]

class XiaomiHAPlugin:
    def __init__(self,name,config_path="data/"):
        self.logger=logging.getLogger('gelonsoft.mihome.XiomiHAPlugin')
        self.name=name
        self.config_path=config_path
        a_yaml_file = open(self.config_path+self.name+"-one-credentials.yaml")
        yaml_config = yaml.load(a_yaml_file, Loader=yaml.FullLoader)
        credentials = yaml_config.get("obmihome")
        self.connector=XiaomiCloudConnector("one", credentials.get("username"), credentials.get("password"), self.config_path)
        self.device_factory=XiaomiDeviceFactory(self.connector)
        self.devices = {}

    def get_device_desc_from_cloud(self):
        result=[]
        for current_server in servers:
            response=self.connector.execute_mi_api("/home/device_list",current_server,{"data": '{"getVirtualModel":false,"getHuamiDevices":0}'})
            if response is not None:
                for device in response["result"]["list"]:
                    device['country']=current_server
                    result.append(device)
        return result


    def load_devices_from_cloud(self):
        if self.connector.logged_in:
            for device in self.get_device_desc_from_cloud():
                self.device_factory.create_device_by_model()

        else:
            self.logger.error("XiaomiCloudConnector is not logged in")

