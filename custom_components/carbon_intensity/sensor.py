from datetime import timedelta
import logging
from .entities.current_rating import CarbonIntensityCurrentRating

from .const import (
  DOMAIN,
  DATA_RATES_COORDINATOR,
  CONFIG_MAIN_REGION
)

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(minutes=1)

async def async_setup_entry(hass, entry, async_add_entities):
  """Setup sensors based on our entry"""

  if CONFIG_MAIN_REGION in entry.data:
    await async_setup_default_sensors(hass, entry, async_add_entities)

async def async_setup_default_sensors(hass, entry, async_add_entities):
  config = dict(entry.data)

  if entry.options:
    config.update(entry.options)
  
  rate_coordinator = hass.data[DOMAIN][DATA_RATES_COORDINATOR]

  await rate_coordinator.async_config_entry_first_refresh()

  region = config[CONFIG_MAIN_REGION]

  entities = [CarbonIntensityCurrentRating(hass, rate_coordinator, region)]

  async_add_entities(entities, True)