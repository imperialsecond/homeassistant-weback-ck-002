"""Support for WeBack robot vacuums."""
from datetime import timedelta
import logging
import voluptuous as vol
from .VacDevice import VacDevice
from .WebackApi import WebackApi
from homeassistant.const import CONF_PASSWORD, CONF_SCAN_INTERVAL, CONF_USERNAME
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import (CoordinatorEntity, DataUpdateCoordinator )

_LOGGER = logging.getLogger(__name__)

DOMAIN = "weback_vacuum"
SCAN_INTERVAL = timedelta(seconds=60)
CONF_REGION = 'region'
CONF_LANGUAGE = 'language'
CONF_APP = 'application'
CONF_CLIENT_ID = 'client_id'
CONF_API_VERS = 'api_version'

DEFAULT_LANGUAGE = "en"
DEFAULT_APP = "WeBack"
DEFAULT_CLIENT_ID = "yugong_app"
DEFAULT_API_VERS = "1.0"

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_USERNAME): cv.string,
                vol.Required(CONF_PASSWORD): cv.string,
                vol.Required(CONF_REGION): cv.string,
                vol.Optional(CONF_LANGUAGE, default=DEFAULT_LANGUAGE): cv.string,
                vol.Optional(CONF_APP, default=DEFAULT_APP): cv.string,
                vol.Optional(CONF_CLIENT_ID, default=DEFAULT_CLIENT_ID): cv.string,
                vol.Optional(CONF_API_VERS, default=DEFAULT_API_VERS): cv.string,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass, config):
    """Set up the Weback component."""
    _LOGGER.info("Creating new Weback Vacuum Robot component")

    hass.data[DOMAIN] = []

    weback_api = WebackApi(
        config[DOMAIN].get(CONF_USERNAME), 
        config[DOMAIN].get(CONF_PASSWORD),
        config[DOMAIN].get(CONF_REGION),
        config[DOMAIN].get(CONF_LANGUAGE),
        config[DOMAIN].get(CONF_APP),
        config[DOMAIN].get(CONF_CLIENT_ID),
        config[DOMAIN].get(CONF_API_VERS),
    )

    _LOGGER.debug("Weback vacuum robots: login started")

    # Login into Weback server's
    log_res = await weback_api.login()
    if not log_res:
        _LOGGER.error("Weback component was unable to login. Failed to setup")
        return False

    # Getting robots lists
    robots = await weback_api.get_robot_list()
    if not robots:
        _LOGGER.error("Weback component was unable to find any robots. Failed to setup")
        return False
    
    _LOGGER.debug(f"Weback vacuum robots: {robots}")

    for robot in robots:
        _LOGGER.info(f'Found robot : {robot["thing_name"]} nickname : {robot["thing_nickname"]}')

        vacuum_device = VacDevice(robot["thing_name"],
                                  robot["thing_nickname"],
                                  robot["sub_type"],
                                  robot["thing_status"],
                                  weback_api.wss_url,
                                  weback_api.region_name,
                                  weback_api.jwt_token)
        hass.data[DOMAIN].append(vacuum_device)

    if hass.data[DOMAIN]:
        _LOGGER.debug("Starting vacuum robot components")
        hass.helpers.discovery.load_platform("vacuum", DOMAIN, {}, config)
    return True
