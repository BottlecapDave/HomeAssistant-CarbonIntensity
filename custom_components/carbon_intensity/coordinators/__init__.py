from datetime import datetime, timedelta
from typing import Callable, Any

from homeassistant.util.dt import (as_utc)
from ..utils.attributes import dict_to_typed_dict

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
  
  event_data = { "rates": current_rates }
  event_data.update(additional_attributes)
  fire_event(current_event_key, dict_to_typed_dict(event_data))
  
  event_data = { "rates": next_rates }
  event_data.update(additional_attributes)
  fire_event(next_event_key, dict_to_typed_dict(event_data))