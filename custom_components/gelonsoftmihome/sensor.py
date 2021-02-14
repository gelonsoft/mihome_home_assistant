"""Platform for sensor integration."""
import json
import logging
from homeassistant.const import TEMP_CELSIUS, STATE_UNKNOWN
from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)

from . import GELONSOFTMIHOME_API

TEMP_SENSOR = {"unit": TEMP_CELSIUS, "name": "temperature"}


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""
    api = hass.data[GELONSOFTMIHOME_API]
    if discovery_info is None:
        return
    devices = []
    for device in discovery_info:
        _LOGGER.warning("Device: %s",device)
        if device["type"] == 'gelonsoftmihome.zhimi.airpurifier.m1':
            devices.append(GelonsoftMiHomeSensor(api, device["guid"], TEMP_SENSOR))
    add_entities(devices)


class GelonsoftMiHomeSensor(Entity):
    """Representation of a Sensor."""

    def __init__(self, api, guid, sensor_type):
        self._device = api.get_device_by_guid(guid=guid)
        self._sensor_type = sensor_type

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self._device.name} {self._sensor_type['name']}"

    @property
    def state(self):
        """Return the state of the sensor."""
        state = STATE_UNKNOWN
        if self._sensor_type == TEMP_SENSOR:
            state = self._device.temperature()

        return state if self._device.isOnline else STATE_UNKNOWN

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._sensor_type["unit"] if self._device.isOnline else None

    def update(self):
        """Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        """
        self._device.update()
