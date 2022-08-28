"""Test the Fully Kiosk Browser diagnostics."""
from unittest.mock import MagicMock

from aiohttp import ClientSession

from homeassistant.components.diagnostics.const import REDACTED
from homeassistant.components.fully_kiosk.const import DOMAIN
from homeassistant.components.fully_kiosk.diagnostics import (
    DEVICE_INFO_TO_REDACT,
    SETTINGS_TO_REDACT,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from tests.common import MockConfigEntry
from tests.components.diagnostics import get_diagnostics_for_device


async def test_diagnostics(
    hass: HomeAssistant,
    hass_client: ClientSession,
    mock_fully_kiosk: MagicMock,
    init_integration: MockConfigEntry,
) -> None:
    """Test Fully Kiosk diagnostics."""

    device_registry = dr.async_get(hass)
    device = device_registry.async_get_device({(DOMAIN, "abcdef-123456")})

    diagnostics = await get_diagnostics_for_device(
        hass, hass_client, init_integration, device
    )

    assert diagnostics
    for key in DEVICE_INFO_TO_REDACT:
        if hasattr(diagnostics, key):
            assert diagnostics[key] == REDACTED
    for key in SETTINGS_TO_REDACT:
        if hasattr(diagnostics["settings"], key):
            assert (
                diagnostics["settings"][key] == REDACTED
                or diagnostics["settings"][key] == ""
            )
