"""Config flow for Switch as X integration."""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import voluptuous as vol

from homeassistant.helpers import helper_config_entry_flow, selector

from . import DOMAIN

CONFIG_FLOW = {
    "user": helper_config_entry_flow.HelperFlowStep(
        vol.Schema(
            {
                vol.Required("entity_id"): selector.selector(
                    {"entity": {"domain": "switch"}}
                ),
                vol.Required("target_domain"): selector.selector(
                    {"select": {"options": ["light"]}}
                ),
            }
        )
    )
}


class SwitchAsXConfigFlowHandler(
    helper_config_entry_flow.HelperConfigFlowHandler, domain=DOMAIN
):
    """Handle a config flow for Switch as X."""

    config_flow = CONFIG_FLOW

    def async_config_entry_title(self, options: Mapping[str, Any]) -> str:
        """Return config entry title."""
        return helper_config_entry_flow.wrapped_entity_config_entry_title(
            self.hass, options["entity_id"]
        )
