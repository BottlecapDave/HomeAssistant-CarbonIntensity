import logging
from datetime import datetime, timedelta
from typing import Callable, Any

from homeassistant.util.dt import (now, as_utc)
from homeassistant.helpers.update_coordinator import (
  DataUpdateCoordinator
)

from ..const import (
  CONFIG_MAIN_REGION,
  COORDINATOR_REFRESH_IN_SECONDS,
  DATA_RATES,
  DATA_RATES_COORDINATOR,
  DOMAIN,
  EVENT_CURRENT_DAY_RATES,
  EVENT_NEXT_DAY_RATES,
  REFRESH_RATE_IN_MINUTES_RATES,
)

from ..api_client import CarbonIntensityApiClient
from . import BaseCoordinatorResult, raise_rate_events

_LOGGER = logging.getLogger(__name__)

class RatesCoordinatorResult(BaseCoordinatorResult):
  last_retrieved: datetime
  rates: list

  def __init__(self, last_retrieved: datetime, request_attempts: int, rates: list):
    super().__init__(last_retrieved, request_attempts, REFRESH_RATE_IN_MINUTES_RATES)
    self.rates = rates

async def async_refresh_rates_data(
    current: datetime,
    client: CarbonIntensityApiClient,
    region: str,
    existing_rates_result: RatesCoordinatorResult,
    fire_event: Callable[[str, "dict[str, Any]"], None],
  ) -> RatesCoordinatorResult: 
  period_from = as_utc(current.replace(hour=0, minute=0, second=0, microsecond=0))

  new_rates: list = None
  if (existing_rates_result is None or
      current >= existing_rates_result.next_refresh or
      existing_rates_result.rates[-1]["from"] < period_from):
    try:
      new_rates = await client.async_get_intensity_and_generation_rates(period_from, region) 
    except:
      _LOGGER.debug(f'Failed to retrieve rates for {region}')
      if (existing_rates_result is not None):
        result = RatesCoordinatorResult(
          existing_rates_result.last_retrieved,
          existing_rates_result.request_attempts + 1,
          existing_rates_result.rates
        )
        _LOGGER.warning(f"Failed to retrieve new carbon intensity rates - using cached rates. Next attempt at {result.next_refresh}")
      else:
        # We want to force into our fallback mode
        result = RatesCoordinatorResult(
          current - timedelta(minutes=REFRESH_RATE_IN_MINUTES_RATES),
          2,
          None
        )
        _LOGGER.warning(f"Failed to retrieve new carbon intensity rates. Next attempt at {result.next_refresh}")

      return result
    
  if new_rates is not None:
    _LOGGER.debug(f'Rates retrieved for {region}')

    raise_rate_events(current,
                      new_rates,
                      { "region": region },
                      fire_event,
                      EVENT_CURRENT_DAY_RATES,
                      EVENT_NEXT_DAY_RATES)
    
    return RatesCoordinatorResult(current, 1, new_rates)
  
  return existing_rates_result

async def async_setup_rates_coordinator(hass, config):
  # Reset data rates as we might have new information
  hass.data[DOMAIN][DATA_RATES_COORDINATOR] = None
  region = config[CONFIG_MAIN_REGION]
  key = DATA_RATES.format(region)
  
  async def async_update_rates_data():
    """Fetch data from API endpoint."""
    current = now()
    client = CarbonIntensityApiClient()
    existing_rates = hass.data[DOMAIN][key] if key in hass.data[DOMAIN] else None

    hass.data[DOMAIN][key] = await async_refresh_rates_data(
      current,
      client,
      region,
      existing_rates,
      hass.bus.async_fire
    )

    return hass.data[DOMAIN][key]

  hass.data[DOMAIN][DATA_RATES_COORDINATOR] = DataUpdateCoordinator(
    hass,
    _LOGGER,
    name=key,
    update_method=async_update_rates_data,
    # Because of how we're using the data, we'll update every minute, but we will only actually retrieve
    # data every 30 minutes
    update_interval=timedelta(seconds=COORDINATOR_REFRESH_IN_SECONDS),
    always_update=True
  )

  await hass.data[DOMAIN][DATA_RATES_COORDINATOR].async_config_entry_first_refresh()