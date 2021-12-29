from homeassistant.components.sensor import SensorEntity

import logging

from . import BaseEntity
from .constants import DOMAIN

from datetime import datetime

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    _LOGGER.debug("Setup sensor: %s", entry)
    entities = []
    entities.append(UtilityMeter(entry))
    entities.append(LastUpdate(entry))
    async_add_entities(entities)
    return True


class UtilityMeter(BaseEntity, SensorEntity):

    def __init__(self, entry):
        super().__init__(entry)
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


class LastUpdate(BaseEntity, SensorEntity):

    def __init__(self, entry):
        super().__init__(entry)
        self.set_ids("last_update", "Last Update")
        self._attr_device_class = "timestamp"
        self._attr_entity_category = "diagnostic"

    @property
    def state(self):
        return datetime.fromtimestamp(self.data.get("last_update"))
