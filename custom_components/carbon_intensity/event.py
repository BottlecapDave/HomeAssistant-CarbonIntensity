import logging

from .const import (
  CONFIG_MAIN_REGION
)

from .entities.rates_current_day import CarbonIntensityCurrentDayRates
from .entities.rates_next_day import CarbonIntensityNextDayRates

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
  """Setup sensors based on our entry"""

  if CONFIG_MAIN_REGION in entry.data:
    await async_setup_main_sensors(hass, entry, async_add_entities)

  return True

async def async_setup_main_sensors(hass, entry, async_add_entities):
  _LOGGER.debug('Setting up main sensors')
  config = dict(entry.data)

  if entry.options:
    config.update(entry.options)

  region = config[CONFIG_MAIN_REGION]
  entities = [
    CarbonIntensityCurrentDayRates(hass, region),
    CarbonIntensityNextDayRates(hass, region),
  ]
  if len(entities) > 0:
    async_add_entities(entities, True)
