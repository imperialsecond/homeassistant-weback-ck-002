"""Platform for climate integration."""

from .ck002 import Ck002Thermostat
from .webackapi import WebackApi
from datetime import timedelta
from homeassistant.components.climate import PLATFORM_SCHEMA
from homeassistant.const import CONF_PASSWORD, CONF_REGION, CONF_USERNAME
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

SCAN_INTERVAL = timedelta(seconds=60)

DOMAIN = 'weback_thermostat'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_USERNAME): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
    vol.Required(CONF_REGION): cv.string,
})

async def setup_entity(api, thing):
    sub_type, name = thing['sub_type'], thing['thing_name']
    if sub_type == 'ck-002s':
        data = await api.user_thing_info_get(sub_type, name)
        return Ck002Thermostat(api, data)
    
    _LOGGER.error("Skipping thing %s with unknown type %s", name, sub_type)
    return None


async def async_setup_entry(hass: HomeAssistant, config_entry, async_add_devices):
    """Set up the platform."""
    config = hass.data[DOMAIN][config_entry.entry_id]

    weback_api = WebackApi(
        config[CONF_USERNAME],
        config[CONF_PASSWORD],
        config[CONF_REGION]
    )

    log_res = await weback_api.login()
    if not log_res:
        _LOGGER.error("Weback component was unable to login. Failed to setup")
        return False

    try:
        things = await weback_api.get_things_list()
    except Exception as e:
        _LOGGER.error("Something went wrong", e)
        return False

    entity_inits = [setup_entity(weback_api, thing) for thing in things]
    entities = [await entity for entity in entity_inits if entity is not None]
    await async_add_devices(entities)

