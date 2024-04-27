from datetime import timedelta
import logging

import voluptuous as vol

from homeassistant.helpers import config_validation as cv, entity_platform
from homeassistant.exceptions import ConfigEntryNotReady

from .const import (
  DOMAIN,
  CONFIG_TARGET_NAME,
  DATA_RATES_COORDINATOR
)
from .target_rates.target_rate import CarbonIntensityTargetRate

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(minutes=1)

async def async_setup_entry(hass, entry, async_add_entities):
  """Setup sensors based on our entry"""

  if CONFIG_TARGET_NAME in entry.data:
    if DOMAIN not in hass.data or DATA_RATES_COORDINATOR not in hass.data[DOMAIN]:
      raise ConfigEntryNotReady
    
    await async_setup_target_sensors(hass, entry, async_add_entities)

  return True

async def async_setup_target_sensors(hass, entry, async_add_entities):
  config = dict(entry.data)

  if entry.options:
    config.update(entry.options)
  
  coordinator = hass.data[DOMAIN][DATA_RATES_COORDINATOR]

  platform = entity_platform.async_get_current_platform()
  platform.async_register_entity_service(
    "update_target_config",
    vol.All(
      vol.Schema(
        {
          vol.Optional("target_hours"): str,
          vol.Optional("target_start_time"): str,
          vol.Optional("target_end_time"): str,
          vol.Optional("target_offset"): str,
          vol.Optional("target_maximum_rate"): str,
        },
        extra=vol.ALLOW_EXTRA,
      ),
      cv.has_at_least_one_key(
        "target_hours", "target_start_time", "target_end_time", "target_offset", "target_maximum_rate"
      ),
    ),
    "async_update_config",
  )

  async_add_entities([CarbonIntensityTargetRate(hass, coordinator, config)], True)
