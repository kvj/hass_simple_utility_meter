from __future__ import annotations
from .constants import DOMAIN, PLATFORMS

import logging

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry):
    _LOGGER.debug("Setup platform: %s", entry)
    for p in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, p))
    return True


async def async_unload_entry(hass, entry):
    for p in PLATFORMS:
        await hass.config_entries.async_forward_entry_unload(entry, p)
    return True


async def async_setup(hass, config) -> bool:
    hass.data[DOMAIN] = dict()

    return True

class BaseEntity:

    def __init__(self, entry):
        self._entry = entry
        self._id = entry.entry_id
        _LOGGER.debug("New BaseEntity: %s, %s, %s", self._id, self.data, self.config)

    @property
    def config(self):
        return self._entry.as_dict().get("data", {})

    @property
    def data(self):
        return self._entry.as_dict().get("options", {})
    
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