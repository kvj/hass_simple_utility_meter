from __future__ import annotations
from .constants import DOMAIN, PLATFORMS
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, CoordinatorEntity

import logging
from datetime import timedelta

_LOGGER = logging.getLogger(__name__)


def get_coordinator(hass, entry):
    return hass.data[DOMAIN][entry.entry_id]

async def async_setup_entry(hass, entry):
    _LOGGER.debug("Setup platform: %s", entry)
    entry.async_on_unload(entry.add_update_listener(update_listener))
    coordinator = Coordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    hass.data[DOMAIN][entry.entry_id] = coordinator
    for p in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, p))
    return True

async def update_listener(hass, entry):
    await get_coordinator(hass, entry).async_request_refresh()


async def async_unload_entry(hass, entry):
    for p in PLATFORMS:
        await hass.config_entries.async_forward_entry_unload(entry, p)
    hass.data[DOMAIN].pop(entry.entry_id)
    return True


async def async_setup(hass, config) -> bool:
    hass.data[DOMAIN] = dict()
    return True

class Coordinator(DataUpdateCoordinator):

    def __init__(self, hass, entry) -> None:
        super().__init__(
            hass, 
            _LOGGER, 
            name="SimpleUtilityMeter", 
            update_method=self.async_update, 
            update_interval=timedelta(seconds=60)
        )
        self.entry = entry

    async def async_update(self):
        _LOGGER.debug("Coordinator update: %s", self.entry.as_dict())
        return self.entry.as_dict()

class BaseEntity(CoordinatorEntity):

    def __init__(self, entry, coordinator):
        super().__init__(coordinator)
        self._entry = entry
        self._id = entry.entry_id
        self._coordinator = coordinator
        _LOGGER.debug("New BaseEntity: %s, %s, %s", self._id, self.data, self.config)

    @property
    def config(self):
        return self._coordinator.data.get("data", {})

    @property
    def data(self):
        return self._coordinator.data.get("options", {})
    
    def set_ids(self, id: str, name: str):
        self.id_suffix = id
        self.name_suffix = name

    @property
    def name(self) -> str:
        return ("%s %s" % (self.config.get("name"), self.name_suffix)).strip()

    @property
    def unique_id(self) -> str:
        return "%s-%s" % (self._id, self.id_suffix)

    @property
    def device_info(self):
        return {
            "identifiers": {("id", self._id)},
            "name": self.config.get("name"),
            "model": "Utility Meter",
            "manufacturer": "Simple Utility Meter"
        }

    async def async_update_data(self, new_data):
        data = {**self.data, **new_data}
        _LOGGER.debug("update_data: %s", data)
        self.hass.config_entries.async_update_entry(self._entry, options=data)
        await self._coordinator.async_request_refresh()