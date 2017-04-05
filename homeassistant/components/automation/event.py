"""
Offer event listening automation rules.

For more details about this automation rule, please refer to the documentation
at https://home-assistant.io/components/automation/#event-trigger
"""
import asyncio
import logging

import voluptuous as vol

from homeassistant.core import callback, CoreState
from homeassistant.const import CONF_PLATFORM, EVENT_HOMEASSISTANT_START
from homeassistant.helpers import config_validation as cv

CONF_EVENT_TYPE = "event_type"
CONF_EVENT_DATA = "event_data"

_LOGGER = logging.getLogger(__name__)

TRIGGER_SCHEMA = vol.Schema({
    vol.Required(CONF_PLATFORM): 'event',
    vol.Required(CONF_EVENT_TYPE): cv.string,
    vol.Optional(CONF_EVENT_DATA): dict,
})


@asyncio.coroutine
def async_trigger(hass, config, action):
    """Listen for events based on configuration."""
    event_type = config.get(CONF_EVENT_TYPE)
    event_data = config.get(CONF_EVENT_DATA)

    if (event_type == EVENT_HOMEASSISTANT_START and
            hass.state == CoreState.starting):
        _LOGGER.warning('Deprecation: Automations should not listen to event '
                        "'homeassistant_start'. Use platform 'homeassistant' "
                        'instead. Feature will be removed in 0.45')
        hass.async_run_job(action, {
            'trigger': {
                'platform': 'event',
                'event': None,
            },
        })
        return lambda: None

    @callback
    def handle_event(event):
        """Listen for events and calls the action when data matches."""
        if not event_data or all(val == event.data.get(key) for key, val
                                 in event_data.items()):
            hass.async_run_job(action, {
                'trigger': {
                    'platform': 'event',
                    'event': event,
                },
            })

    return hass.bus.async_listen(event_type, handle_event)
