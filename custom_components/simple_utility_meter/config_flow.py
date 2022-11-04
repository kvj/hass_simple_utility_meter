from homeassistant import config_entries
import homeassistant.helpers.config_validation as cv
from .constants import DOMAIN

import logging
import voluptuous as vol
from datetime import datetime

_LOGGER = logging.getLogger(__name__)

def _validate(user_input):
    errors = {}
    return errors

unit_types = {"kWh": "kWh", "m³": "m³", "ft³": "ft³", "l": "l"}
device_types = {None: "None", "energy": "Energy", "gas": "Gas", "water": "Water"}
measure_type = {"total": "Always total value", "total_increasing": "Total value (with reset)"}

def _gen_init_schema(data: dict):
    return vol.Schema({
        vol.Required("name", default=data.get("name")): cv.string,
        vol.Required("measure_type", default=data.get("measure_type")): vol.In(measure_type),
        vol.Required("type", default=data.get("type")): vol.In(device_types),
        vol.Required("unit", default=data.get("unit")): vol.In(unit_types),
        vol.Required("value", default=data.get("value")): cv.positive_float,
    })

def _gen_options_schema(data: dict):
    return vol.Schema({
        vol.Required("value", default=data.get("value")): cv.positive_float,
        vol.Required("measure_type", default=data.get("measure_type")): vol.In(measure_type),
        vol.Required("type", default=data.get("type")): vol.In(device_types),
    })


class ConfigFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):

    def async_get_options_flow(config_entry):
        return OptionsFlowHandler(config_entry)

    async def async_step_user(self, user_input):
        errors = None

        _LOGGER.debug(f"Input: {user_input}")
        if user_input:
            errors = _validate(user_input)
            if len(errors) == 0:
                return self.async_create_entry(
                    title=user_input.get("name"),
                    options=dict(
                        value=user_input.get("value"), 
                        type=user_input.get("type"),
                        measure_type=user_input.get("measure_type"),
                        last_update=datetime.now().timestamp(),
                    ),
                    data=dict(
                        name=user_input.get("name"), 
                        unit=user_input.get("unit"), 
                    ),
                )

        if not user_input:
            user_input = dict(name="My Meter", unit="kWh", value=0, type=None, measure_type="total")

        return self.async_show_form(
            step_id="user", data_schema=_gen_init_schema(user_input), errors=errors
        )

class OptionsFlowHandler(config_entries.OptionsFlow):

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        _LOGGER.debug(f"OptionsFlowHandler: {user_input} {self.config_entry}")
        errors = None
        if user_input:
            errors = _validate(user_input)
            if len(errors) == 0:
                return self.async_create_entry(title="", data=dict(
                    type=user_input.get("type"),
                    measure_type=user_input.get("measure_type"),
                    value=user_input.get("value"), 
                    last_update=datetime.now().timestamp(),
                ))
        else:
            user_input = self.config_entry.as_dict()["options"]

        return self.async_show_form(
            step_id="init", data_schema=_gen_options_schema(user_input), errors=errors
        )
