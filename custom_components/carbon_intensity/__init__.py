import logging
from datetime import timedelta
from homeassistant.util.dt import (utcnow, as_utc, parse_datetime)
import asyncio

from .const import (
  DOMAIN,

  CONFIG_MAIN_REGION,
  
  CONFIG_TARGET_NAME,

  DATA_CONFIG,
  DATA_RATES_COORDINATOR,
  DATA_RATES,
)

from .api_client import CarbonIntensityApiClient

from homeassistant.helpers.update_coordinator import (
  DataUpdateCoordinator
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry):
  """This is called from the config flow."""
  hass.data.setdefault(DOMAIN, {})

  if CONFIG_MAIN_REGION in entry.data:
    setup_dependencies(hass, entry.data)

    # Forward our entry to setup our default sensors
    # hass.async_create_task(
    #   hass.config_entries.async_forward_entry_setup(entry, "sensor")
    # )
  elif CONFIG_TARGET_NAME in entry.data:
    # Forward our entry to setup our target rate sensors
    hass.async_create_task(
      hass.config_entries.async_forward_entry_setup(entry, "binary_sensor")
    )
  
  entry.async_on_unload(entry.add_update_listener(options_update_listener))

  return True

def setup_dependencies(hass, config):
  """Setup the coordinator and api client which will be shared by various entities"""

  hass.data[DOMAIN][DATA_CONFIG] = config

  if DATA_RATES_COORDINATOR not in hass.data[DOMAIN]:
    async def async_update_rates_data():
      """Fetch data from API endpoint."""
      # Only get data every half hour or if we don't have any data
      if (DATA_RATES not in hass.data[DOMAIN] or (utcnow().minute % 30) == 0 or len(hass.data[DOMAIN][DATA_RATES]) == 0):

        utc_now = utcnow()
        period_from = as_utc(parse_datetime(utc_now.strftime("%Y-%m-%dT%H:%M:%SZ")))

        client = CarbonIntensityApiClient()
        hass.data[DOMAIN][DATA_RATES] = await client.async_get_intensity_and_generation_rates(period_from, config[CONFIG_MAIN_REGION]) 
      
      return hass.data[DOMAIN][DATA_RATES]

    hass.data[DOMAIN][DATA_RATES_COORDINATOR] = DataUpdateCoordinator(
      hass,
      _LOGGER,
      name="rates",
      update_method=async_update_rates_data,
      # Because of how we're using the data, we'll update every minute, but we will only actually retrieve
      # data every 30 minutes
      update_interval=timedelta(minutes=1),
    )

async def options_update_listener(hass, entry):
  """Handle options update."""
  await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass, entry):
    """Unload a config entry."""
    if CONFIG_MAIN_REGION in entry.data:
      target_domain = "sensor"
    elif CONFIG_TARGET_NAME in entry.data:
      target_domain = "binary_sensor"

    unload_ok = all(
        await asyncio.gather(
            *[hass.config_entries.async_forward_entry_unload(entry, target_domain)]
        )
    )

    return unload_ok