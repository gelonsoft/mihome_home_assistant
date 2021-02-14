import abc
class AbstractMiDevice:
    def __init__(self):
        pass

    @abc.abstractmethod
    @staticmethod
    def model_type():
        pass


    @abc.abstractmethod
    def create_device_by_content(self,content):
        pass

    def load_basic_info_from_content(self,content):
        self.did=content['did']
        self.model=content['model']
        self.name=content['name']
        self.uid=content['uid']
        self.country=content['country']
        self.isOnline=content['isOnline']
        self.fullcontent=content

    @abc.abstractmethod
    def convert_to_ha_devices(self):
        pass

    def update(self):
        pass
