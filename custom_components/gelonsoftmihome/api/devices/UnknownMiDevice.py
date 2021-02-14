import AbstractMiDevice


class UnknownMiDevice(AbstractMiDevice):
    def __init__(self):
        pass

    @staticmethod
    def model_type():
        return "unknown"

    def create_device_by_content(self, content):
        self.load_basic_info_from_content(content)

    def convert_to_ha_devices(self):
        return None