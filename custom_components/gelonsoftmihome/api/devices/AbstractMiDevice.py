import abc
import datetime
import json
import logging
from typing import Optional

from custom_components.gelonsoftmihome.api.XiaomiCloudConnector import XiaomiCloudConnector


class AbstractMiDevice:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._spec = None
        self.did = None
        self.model = None
        self.name = None
        self.uid = None
        self.country = None
        self.isOnline = None
        self.full_content = None
        self._min_seconds_between_updates = 60
        self._last_update_time = datetime.datetime.now()
        self._values_cache = {}
        self._not_in_update = True
        self._cloud_connector: XiaomiCloudConnector = None
        self._type_map = {}

    @abc.abstractmethod
    def model_type(self):
        pass

    @abc.abstractmethod
    def create_device_by_content(self, content):
        pass

    def load_basic_info_from_content(self, content):
        self.did = content['did']
        self.model = content['model']
        self.name = content['name']
        self.uid = content['uid']
        self.country = content['country']
        self.isOnline = content['isOnline']
        self.full_content = content

    @abc.abstractmethod
    def convert_to_ha_devices(self):
        pass

    def set_cloud_connector(self, connector: XiaomiCloudConnector):
        self._cloud_connector = connector

    def can_update(self):
        seconds = (datetime.datetime.now() - self._last_update_time).total_seconds()
        if seconds < self._min_seconds_between_updates:
            return True

    def set_spec(self, spec):
        self._spec = spec

    def identify_units(self, props) -> Optional[str]:
        result = None
        unit = props.get('punit')
        if unit is not None:
            if unit == "celsius":
                result = "°C"
            if unit == "hours":
                result = "h"
            if unit == "percentage":
                result = "%"
            if unit == "seconds":
                result = "s"
            if unit == "minutes":
                result = "min"
            if unit == "days":
                result = "d"
            if unit == "kelvin":
                result = "K"
            if unit == "pascal":
                result = "Pa"
            if unit == "arcdegrees":
                result = "°"
            if unit == "rgb":
                result = None
            if unit == "watt":
                result = "W"
            if unit == "litre":
                result = "L"
            if unit == "ppm":
                result = "ppm"
            if unit == "lux":
                result = "lx"
            if unit == "mg/m3":
                result = "mg/m³"
        return result

    def basic_convert_to_ha_devices(self):
        result = {}
        if self.isOnline:
            result['sensor'] = []
            props = self._spec.get('properties')
            if props is not None:
                for p in self._spec.get('properties'):
                    _type = 'gelonsoftmihome.' + p.get('id')
                    self._values_cache[_type] = None
                    self._type_map[f"{p.get('siid')}.{p.get('piid')}"] = _type
                    val = {}
                    val['type'] = _type
                    val['did'] = self.did
                    val['unique_id'] = _type + "." + self.did
                    val['name'] = f"{self.name} {p.get('pdescription')} - {p.get('sdescription')}"
                    val['units'] = self.identify_units(p)
                    result['sensor'].append(val)
        return result

    def get_value(self, _type):
        if _type is not None:
            return self._values_cache[_type]
        else:
            return None

    def update(self):
        if self.can_update() and self._not_in_update:
            try:
                self._not_in_update = False
                _data = {}
                _data['params'] = []
                self.logger.warning("Device %s update started", self.did)
                for p in self._spec.get('properties'):
                    _type = 'gelonsoftmihome.' + p.get('id')
                    _data['params'].append({'did': self.did, 'siid': p.get('siid'), 'piid': p.get('piid')})
                _data['datasource'] = 3
                result = self._cloud_connector.get_device_data_miot(self.country, _data)
                self.logger.warning("Device %s update data is %s", self.did, json.dumps(result))
                self.logger.warning("Device %s update type_map is %s", self.did, json.dumps(self._type_map))
                for r in result:
                    if r.get('code') == 0:
                        _type = self._type_map.get(f"{r.get('siid')}.{r.get('piid')}")
                        if _type is not None:
                            self._values_cache[_type] = r.get('value')
                self._last_update_time = datetime.datetime.now()
                self.logger.warning("Device %s updated with %s", self.did, json.dumps(self._values_cache))
            finally:
                self._not_in_update = True

    @abc.abstractmethod
    def load_from_content(self, content):
        pass
