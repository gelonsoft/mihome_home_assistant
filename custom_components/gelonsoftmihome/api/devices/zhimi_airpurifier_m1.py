from . import AbstractMiDevice
import logging


class zhimi_airpurifier_m1(AbstractMiDevice.AbstractMiDevice):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.type = 'gelonsoftmihome.' + self.model_type()
        self.isOnline = False
        self._temperature = None
        pass

    @staticmethod
    def model_type():
        return "zhimi.airpurifier.m1"

    def get_id(self):
        return self.type + ":" + self.did

    def convert_to_ha_devices(self):
        result = {}
        if self.isOnline:
            result['sensor'] = {type: self.type, 'guid': self.did}
        return result

    def temperature(self):
        return self._temperature

    def load_from_content(self,content):
        self.load_basic_info_from_content(content)
        self._temperature = self.fullcontent['prop']['aqi']