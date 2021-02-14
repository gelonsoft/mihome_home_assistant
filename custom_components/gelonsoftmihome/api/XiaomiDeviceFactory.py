import inspect
import sys
import logging

from gelonsoftmihome.api.devices import AbstractMiDevice


class XiaomiDeviceFactory:
    def __init__(self, xiaomiCloudConnector):
        self.xiaomi_cloud_connector = xiaomiCloudConnector
        self.device_classes = self.get_device_classes()
        self.logger = logging.getLogger('gelonsoftmihome.api.XiaomiDeviceFactory')
        self.device_classes = self.get_device_classes()

    def get_device_classes(self):
        result = {}
        for name, obj in inspect.getmembers(sys.modules["gelonsoftmihome.api.devices"]):
            if inspect.isclass(obj) and issubclass(obj, type(AbstractMiDevice)) and name != "AbstractMiDevice":
                try:
                    print(name)
                    print(obj)
                    print(type(obj))
                    model = obj.model
                    result[model] = obj
                    self.logger.info("Registered model %s as device type %s", model, obj)
                except:
                    pass
        return result

    def create_device_by_model(self, model):
        if model in self.device_classes:
            return self.device_classes[model]()
        else:
            return self.device_classes['unknown']()

    def create_device_by_content(self, content: dict) -> AbstractMiDevice:
        model = content['model']
        if not model:
            return None
        else:
            result = self.create_device_by_model(model)
            result.load_from_content(content)
            return result
