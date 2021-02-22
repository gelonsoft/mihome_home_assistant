from . import AbstractMiDevice
import logging


class zhimi_airpurifier_m1(AbstractMiDevice.AbstractMiDevice):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.devtype = 'gelonsoftmihome.' + self.model_type()
        pass

    @staticmethod
    def model_type():
        return "zhimi.airpurifier.m1XXXXX"

    def get_id(self):
        return self.devtype + ":" + self.did

    def convert_to_ha_devices(self):
        result = self.basic_convert_to_ha_devices()
        return result

    def load_from_content(self, content):
        self.load_basic_info_from_content(content)
