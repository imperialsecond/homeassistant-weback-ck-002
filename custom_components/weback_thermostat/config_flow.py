"""Config flow for Hello World integration."""

from .climate import DOMAIN
from .webackapi import WebackApi
from homeassistant import config_entries, exceptions
from homeassistant.const import CONF_PASSWORD, CONF_REGION, CONF_USERNAME
import logging
import voluptuous as vol

_LOGGER = logging.getLogger(__name__)
DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_USERNAME): str,
    vol.Required(CONF_REGION): str,
    vol.Required(CONF_PASSWORD): str
})

async def validate_input(hass, input):
    api = WebackApi(input[CONF_USERNAME], input[CONF_PASSWORD], input[CONF_REGION])
    if not await api.login():
        raise Exception("failed to login")
    return input

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for weback_thermostat."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
                return self.async_create_entry(title=user_input[CONF_USERNAME], data=info)
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "cannot_connect"

        # If there is no user input or there were errors, show the form again, including any errors that were found with the input.
        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )
