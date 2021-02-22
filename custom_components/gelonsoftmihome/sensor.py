"""Platform for sensor integration."""
import json
import logging
from homeassistant.const import TEMP_CELSIUS, STATE_UNKNOWN
from homeassistant.helpers.entity import Entity

import logging

from .api.devices.AbstractMiDevice import AbstractMiDevice
from .const import DOMAIN, GELONSOFTMIHOME_API

_LOGGER = logging.getLogger(__name__)

TEMP_SENSOR = {"unit": TEMP_CELSIUS, "name": "temperature"}

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""
    api = hass.data[GELONSOFTMIHOME_API]
    if discovery_info is None:
        return
    devices = []
    for device in discovery_info:
        _LOGGER.warning("Device: %s", device)
        _device=api.get_device_by_did(did=device.get("did"))
        devices.append(GelonsoftMiHomeSensor(api, _device, device.get("type")))
    add_entities(devices)


class GelonsoftMiHomeSensor(Entity):
    """Representation of a Sensor."""

    def __init__(self, api, _device: AbstractMiDevice, _type):
        self._device = _device
        self._type = _type

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self._device.name} {self._type}"

    @property
    def state(self):
        """Return the state of the sensor."""
        state = STATE_UNKNOWN
        v = self._device.get_value(self._device.get_value(self._type))

        return state if self._device.isOnline else STATE_UNKNOWN

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return None
        #return self._sensor_type["unit"] if self._device.isOnline else None

    def update(self):
        """Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        """
        self._device.update()