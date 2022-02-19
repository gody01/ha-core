"""Test the EcoVent_v2 config flow."""
from unittest.mock import patch

from homeassistant import config_entries
from homeassistant.components.ecovent_v2.config_flow import CannotConnect, InvalidAuth
from homeassistant.components.ecovent_v2.const import DOMAIN
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import RESULT_TYPE_CREATE_ENTRY, RESULT_TYPE_FORM


async def test_form(hass: HomeAssistant) -> None:
    """Test we get the form."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == RESULT_TYPE_FORM
    assert result["errors"] is None

    with patch(
        "homeassistant.components.ecovent_v2.config_flow.PlaceholderHub.authenticate",
        return_value=True,
    ), patch(
        "homeassistant.components.ecovent_v2.async_setup_entry",
        return_value=True,
    ) as mock_setup_entry:
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                "host": "1.1.1.1",
                "port": 4000,
                "fan_id": "DEFAULT_DEVICEID",
                "password": "test-password",
                "name": "Vento Expert Fan",
            },
        )
    assert result2["type"] == RESULT_TYPE_CREATE_ENTRY
    assert result2["title"] == "Vento Expert Fan"
    assert result2["data"] == {
        "host": "1.1.1.1",
        "port": 4000,
        "fan_id": "DEFAULT_DEVICEID",
        "password": "test-password",
        "name": "Vento Expert Fan",
    }
    assert len(mock_setup_entry.mock_calls) == 1


async def test_form_invalid_auth(hass: HomeAssistant) -> None:
    """Test we handle invalid auth."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch(
        "homeassistant.components.ecovent_v2.config_flow.PlaceholderHub.authenticate",
        side_effect=InvalidAuth,
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                "host": "1.1.1.1",
                "port": 4000,
                "fan_id": "DEFAULT_DEVICEID",
                "password": "test-password",
                "name": "Vento Expert Fan",
            },
        )

    assert result2["type"] == RESULT_TYPE_FORM
    assert result2["errors"] == {"base": "invalid_auth"}


async def test_form_cannot_connect(hass: HomeAssistant) -> None:
    """Test we handle cannot connect error."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch(
        "homeassistant.components.ecovent_v2.config_flow.PlaceholderHub.authenticate",
        side_effect=CannotConnect,
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                "host": "1.1.1.1",
                "port": 4000,
                "fan_id": "DEFAULT_DEVICEID",
                "password": "test-password",
                "name": "Vento Expert Fan",
            },
        )

    assert result2["type"] == RESULT_TYPE_FORM
    assert result2["errors"] == {"base": "cannot_connect"}
