from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.const import (
    UnitOfTemperature,
)

class Ck002Thermostat(ClimateEntity):
    _attr_hvac_modes = [HVACMode.OFF, HVACMode.HEAT, HVACMode.AUTO]
    _attr_preset_modes = ['Manual', 'Automatic']
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
    )
    _attr_has_entity_name = True

    def __init__(self, api, data):
        self.api = api
        self.status = data['thing_status']
        self.subtype = data['sub_type']
        self.thing_name = data['thing_name']
        self._attr_name = data['thing_nickname']

    @property
    def hvac_mode(self) -> HVACMode | None:
        """Return hvac operation ie. heat, cool mode."""
        # TODO
        return HVACMode.HEAT

    @property
    def hvac_action(self) -> HVACAction | None:
        return HVACAction.HEATING if self.status['working_status'] == 'on' else HVACAction.IDLE

    @property
    def current_temperature(self) -> float | None:
        return self.status['air_tem'] / 10

    @property
    def target_temperature(self) -> float | None:
        return self.status['set_tem'] / 2

    @property
    def temperature_unit(self) -> str:
        return UnitOfTemperature.CELSIUS

    async def async_update(self):
        self.status = await self.api.user_thing_info_get(self.sub_type, self.thing_name)

