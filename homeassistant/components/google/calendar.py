"""Support for Google Calendar Search binary sensors."""
from __future__ import annotations

import copy
from datetime import datetime, timedelta
import logging
from typing import Any

from httplib2 import ServerNotFoundError

from homeassistant.components.calendar import (
    ENTITY_ID_FORMAT,
    CalendarEventDevice,
    calculate_offset,
    is_offset_reached,
)
from homeassistant.const import CONF_DEVICE_ID, CONF_ENTITIES, CONF_NAME, CONF_OFFSET
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import generate_entity_id
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.util import Throttle

from . import (
    CONF_CAL_ID,
    CONF_IGNORE_AVAILABILITY,
    CONF_SEARCH,
    CONF_TRACK,
    DATA_SERVICE,
    DEFAULT_CONF_OFFSET,
    DOMAIN,
)
from .api import GoogleCalendarService

_LOGGER = logging.getLogger(__name__)

DEFAULT_GOOGLE_SEARCH_PARAMS = {
    "orderBy": "startTime",
    "singleEvents": True,
}

MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=15)

# Events have a transparency that determine whether or not they block time on calendar.
# When an event is opaque, it means "Show me as busy" which is the default.  Events that
# are not opaque are ignored by default.
TRANSPARENCY = "transparency"
OPAQUE = "opaque"


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    disc_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the calendar platform for event devices."""
    if disc_info is None:
        return

    if not any(data[CONF_TRACK] for data in disc_info[CONF_ENTITIES]):
        return

    calendar_service = hass.data[DOMAIN][DATA_SERVICE]
    entities = []
    for data in disc_info[CONF_ENTITIES]:
        if not data[CONF_TRACK]:
            continue
        entity_id = generate_entity_id(
            ENTITY_ID_FORMAT, data[CONF_DEVICE_ID], hass=hass
        )
        entity = GoogleCalendarEventDevice(
            calendar_service, disc_info[CONF_CAL_ID], data, entity_id
        )
        entities.append(entity)

    add_entities(entities, True)


class GoogleCalendarEventDevice(CalendarEventDevice):
    """A calendar event device."""

    def __init__(
        self,
        calendar_service: GoogleCalendarService,
        calendar_id: str,
        data: dict[str, Any],
        entity_id: str,
    ) -> None:
        """Create the Calendar event device."""
        self.data = GoogleCalendarData(
            calendar_service,
            calendar_id,
            data.get(CONF_SEARCH),
            data.get(CONF_IGNORE_AVAILABILITY, False),
        )
        self._event: dict[str, Any] | None = None
        self._name: str = data[CONF_NAME]
        self._offset = data.get(CONF_OFFSET, DEFAULT_CONF_OFFSET)
        self._offset_reached = False
        self.entity_id = entity_id

    @property
    def extra_state_attributes(self) -> dict[str, bool]:
        """Return the device state attributes."""
        return {"offset_reached": self._offset_reached}

    @property
    def event(self) -> dict[str, Any] | None:
        """Return the next upcoming event."""
        return self._event

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self._name

    async def async_get_events(
        self, hass: HomeAssistant, start_date: datetime, end_date: datetime
    ) -> list[dict[str, Any]]:
        """Get all events in a specific time frame."""
        return await self.data.async_get_events(hass, start_date, end_date)

    def update(self) -> None:
        """Update event data."""
        self.data.update()
        event = copy.deepcopy(self.data.event)
        if event is None:
            self._event = event
            return
        event = calculate_offset(event, self._offset)
        self._offset_reached = is_offset_reached(event)
        self._event = event


class GoogleCalendarData:
    """Class to utilize calendar service object to get next event."""

    def __init__(
        self,
        calendar_service: GoogleCalendarService,
        calendar_id: str,
        search: str | None,
        ignore_availability: bool,
    ) -> None:
        """Set up how we are going to search the google calendar."""
        self.calendar_service = calendar_service
        self.calendar_id = calendar_id
        self.search = search
        self.ignore_availability = ignore_availability
        self.event: dict[str, Any] | None = None

    def _event_filter(self, event: dict[str, Any]) -> bool:
        """Return True if the event is visible."""
        if self.ignore_availability:
            return True
        return event.get(TRANSPARENCY, OPAQUE) == OPAQUE

    async def async_get_events(
        self, hass: HomeAssistant, start_date: datetime, end_date: datetime
    ) -> list[dict[str, Any]]:
        """Get all events in a specific time frame."""
        event_list: list[dict[str, Any]] = []
        page_token: str | None = None
        while True:
            try:
                items, page_token = await self.calendar_service.async_list_events(
                    self.calendar_id,
                    start_time=start_date,
                    end_time=end_date,
                    search=self.search,
                    page_token=page_token,
                )
            except ServerNotFoundError as err:
                _LOGGER.error("Unable to connect to Google: %s", err)
                return []

            event_list.extend(filter(self._event_filter, items))
            if not page_token:
                break
        return event_list

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self) -> None:
        """Get the latest data."""
        try:
            items, _ = self.calendar_service.list_events(
                self.calendar_id, search=self.search
            )
        except ServerNotFoundError as err:
            _LOGGER.error("Unable to connect to Google: %s", err)
            return

        valid_events = filter(self._event_filter, items)
        self.event = next(valid_events, None)
