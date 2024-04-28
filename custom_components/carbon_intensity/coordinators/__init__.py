import logging
from datetime import datetime, timedelta
from typing import Callable, Any

from homeassistant.util.dt import (as_utc)
from ..utils.attributes import dict_to_typed_dict
from ..utils.requests import calculate_next_refresh

_LOGGER = logging.getLogger(__name__)

class BaseCoordinatorResult:
  last_retrieved: datetime
  next_refresh: datetime
  request_attempts: int
  refresh_rate_in_minutes: int

  def __init__(self, last_retrieved: datetime, request_attempts: int, refresh_rate_in_minutes: int):
    self.last_retrieved = last_retrieved
    self.request_attempts = request_attempts
    self.next_refresh = calculate_next_refresh(last_retrieved, request_attempts, refresh_rate_in_minutes)
    _LOGGER.debug(f'last_retrieved: {last_retrieved}; request_attempts: {request_attempts}; refresh_rate_in_minutes: {refresh_rate_in_minutes}; next_refresh: {self.next_refresh}')

def raise_rate_events(now: datetime,
                      rates: list, 
                      additional_attributes: "dict[str, Any]",
                      fire_event: Callable[[str, "dict[str, Any]"], None],
                      current_event_key: str,
                      next_event_key: str):
  
  today_start = as_utc(now.replace(hour=0, minute=0, second=0, microsecond=0))
  today_end = today_start + timedelta(days=1)

  previous_rates = []
  current_rates = []
  next_rates = []

  for rate in rates:
    if (rate["from"] < today_start):
      previous_rates.append(rate)
    elif (rate["from"] >= today_end):
      next_rates.append(rate)
    else:
      current_rates.append(rate)
  
  event_data = dict_to_typed_dict({ "rates": current_rates })
  event_data.update(additional_attributes)
  fire_event(current_event_key, event_data)
  
  event_data = dict_to_typed_dict({ "rates": next_rates })
  event_data.update(additional_attributes)
  fire_event(next_event_key, event_data)