import logging

from . import AbstractMiDevice
import abc


class UnknownMiDevice(AbstractMiDevice.AbstractMiDevice):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)

    @staticmethod
    def model_type():
        return "unknown"

    def convert_to_ha_devices(self):
        result = self.basic_convert_to_ha_devices()
        return result

    def load_from_content(self,content):
        self.load_basic_info_from_content(content)