"""Config flow for the Teltonika Telematics Tracker integration."""

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers import selector

from .const import DOMAIN

DEFAULT_PORT = 25001

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(
            "port",
            default=DEFAULT_PORT,
        ): selector.NumberSelector(
            selector.NumberSelectorConfig(
                min=1,
                max=65535,
                mode=selector.NumberSelectorMode.BOX,
            )
        ),
    }
)


class TeltonikaTrackerConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Teltonika Telematics Tracker."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        if user_input is not None:
            return self.async_create_entry(
                title="Teltonika Tracker Integration",
                data=user_input,
            )

        return self.async_show_form(step_id="user", data_schema=STEP_USER_DATA_SCHEMA)
