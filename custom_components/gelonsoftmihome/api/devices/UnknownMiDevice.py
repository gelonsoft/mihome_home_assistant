from . import AbstractMiDevice
import abc


class UnknownMiDevice(AbstractMiDevice.AbstractMiDevice):
    def __init__(self):
        pass

    @staticmethod
    def model_type():
        return "unknown"

    def convert_to_ha_devices(self):
        return None

    def load_from_content(self,content):
        self.load_basic_info_from_content(content)
