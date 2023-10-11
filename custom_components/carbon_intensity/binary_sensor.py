from datetime import timedelta
import logging
from .target_rates.target_rate import CarbonIntensityTargetRate

from homeassistant.exceptions import ConfigEntryNotReady

from .const import (
  DOMAIN,

  CONFIG_TARGET_NAME,

  DATA_RATES_COORDINATOR
)

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

  async_add_entities([CarbonIntensityTargetRate(coordinator, config)], True)
