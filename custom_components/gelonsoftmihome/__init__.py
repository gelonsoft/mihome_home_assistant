import logging
import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from datetime import timedelta
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD, CONF_SCAN_INTERVAL, CONF_FILE_PATH
from homeassistant.helpers import discovery

from custom_components.gelonsoftmihome.api.XiaomiHAPlugin import XiaomiHAPlugin

DOMAIN = 'gelonsoftmihome'
GELONSOFTMIHOME_API = 'gelonsoftmihome'

DEFAULT_SCAN_INTERVAL = timedelta(minutes=10)
DEFAULT_AUTH_FNAME = "gelonsoftmihome_auth"

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_USERNAME): cv.string,
                vol.Required(CONF_PASSWORD): cv.string,
                vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): cv.time_period,
                vol.Optional(CONF_FILE_PATH, default=DEFAULT_AUTH_FNAME): cv.string,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


def setup(hass, config):
    """Set up GelonsoftMiHome Component."""
    #auth_fname = hass.config.path("gelonsoftmihome_auth") if config[DOMAIN][CONF_FILE_PATH] == DEFAULT_AUTH_FNAME else config[DOMAIN][CONF_FILE_PATH]
    api = XiaomiHAPlugin(
        config[DOMAIN][CONF_USERNAME],
        config[DOMAIN][CONF_PASSWORD],
        config[DOMAIN][CONF_FILE_PATH]
#        min_update_interval_sec=(config[DOMAIN][CONF_SCAN_INTERVAL]).seconds
    )
    assert api.authorization, "Couldn't get authorisation data!"
    _LOGGER.info(f"Api initialized with authorization {api.authorization}")
    hass.data[GELONSOFTMIHOME_API] = api

    for device_type, devices in api.ha_devices.items():
        discovery.load_platform(hass, device_type, DOMAIN, devices, config)
        _LOGGER.info(f"Found {len(devices)} {device_type} devices")
    # Return boolean to indicate that initialization was successful.
    return True