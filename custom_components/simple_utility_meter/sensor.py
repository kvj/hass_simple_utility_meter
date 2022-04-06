from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers import config_validation as cv, entity_platform
from homeassistant.helpers.entity import EntityCategory
import voluptuous as vol

import logging

from . import BaseEntity, get_coordinator
from .constants import DOMAIN

from datetime import datetime

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    _LOGGER.debug("Setup sensor: %s", entry)
    coordinator = get_coordinator(hass, entry)
    entities = []
    platform = entity_platform.async_get_current_platform()
    entities.append(UtilityMeter(entry, coordinator))
    entities.append(LastUpdate(entry, coordinator))
    async_add_entities(entities)
    platform.async_register_entity_service(
        "update_meter_value",
        {vol.Required("value"): cv.positive_float},
        "async_update_value",
    )
    return True


class UtilityMeter(BaseEntity, SensorEntity):

    def __init__(self, entry, coordinator):
        super().__init__(entry, coordinator)
        self.set_ids("value", "")
        self._attr_state_class = "total_increasing"
        self._attr_device_class = self.config.get("type")

    @property
    def state_class(self):
        return self.data.get("measure_type", "total")

    @property
    def device_class(self):
        return self.data.get("type")

    @property
    def native_unit_of_measurement(self):
        return self.config.get("unit")

    @property
    def native_value(self):
        return self.data.get("value")

    @property
    def state(self):
        _LOGGER.debug("UtilityMeter[%s] state: %s", self.name, self.data)
        return self.native_value

    async def async_update_value(self, value):
        await self.async_update_data(dict(
            value=value,
            last_update=datetime.now().timestamp(),
        ))


class LastUpdate(BaseEntity, SensorEntity):

    def __init__(self, entry, coordinator):
        super().__init__(entry, coordinator)
        self.set_ids("last_update", "Last Update")
        self._attr_device_class = "timestamp"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def state(self):
        return datetime.fromtimestamp(self.data.get("last_update"))
