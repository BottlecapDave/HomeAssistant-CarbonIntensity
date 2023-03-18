from datetime import datetime, timedelta
import math
from homeassistant.util.dt import (as_utc, parse_datetime)
from ..utils import (apply_offset)
import logging

_LOGGER = logging.getLogger(__name__)

def __get_applicable_rates(current_date: datetime, target_start_time: str, target_end_time: str, rates, is_rolling_target: bool):
  if (target_start_time is not None):
    target_start = parse_datetime(current_date.strftime(f"%Y-%m-%dT{target_start_time}:00%z"))
  else:
    target_start = parse_datetime(current_date.strftime(f"%Y-%m-%dT00:00:00%z"))

  if (target_end_time is not None):
    target_end = parse_datetime(current_date.strftime(f"%Y-%m-%dT{target_end_time}:00%z"))
  else:
    target_end = parse_datetime(current_date.strftime(f"%Y-%m-%dT00:00:00%z")) + timedelta(days=1)

  target_start = as_utc(target_start)
  target_end = as_utc(target_end)

  if (target_start >= target_end):
    _LOGGER.debug(f'{target_start} is after {target_end}, so setting target end to tomorrow')
    if target_start > current_date:
      target_start = target_start - timedelta(days=1)
    else:
      target_end = target_end + timedelta(days=1)

  # If our start date has passed, reset it to current_date to avoid picking a slot in the past
  if (is_rolling_target == True and target_start < current_date and current_date < target_end):
    _LOGGER.debug(f'Rolling target and {target_start} is in the past. Setting start to {current_date}')
    target_start = current_date

  # If our start and end are both in the past, then look to the next day
  if (target_start < current_date and target_end < current_date):
    target_start = target_start + timedelta(days=1)
    target_end = target_end + timedelta(days=1)

  _LOGGER.debug(f'Finding rates between {target_start} and {target_end}')

  # Retrieve the rates that are applicable for our target rate
  applicable_rates = []
  if rates != None:
    for rate in rates:
      if rate["from"] >= target_start and (target_end == None or rate["to"] <= target_end):
        applicable_rates.append(rate)

  # Make sure that we have enough rates that meet our target period
  date_diff = target_end - target_start
  hours = (date_diff.days * 24) + (date_diff.seconds // 3600)
  periods = hours * 2
  if len(applicable_rates) < periods:
    _LOGGER.debug(f'Incorrect number of periods discovered. Require {periods}, but only have {len(applicable_rates)}')
    return None

  return applicable_rates

def __get_intensity(rate):
  return rate["intensity_forecast"]

def __get_to(rate):
  return rate["to"]

def calculate_continuous_times(current_date: datetime, target_start_time: str, target_end_time: str, target_hours: float, rates, is_rolling_target = True):
  applicable_rates = __get_applicable_rates(current_date, target_start_time, target_end_time, rates, is_rolling_target)
  if (applicable_rates is None):
    return []

  applicable_rates_count = len(applicable_rates)
  total_required_rates = math.ceil(target_hours * 2)

  best_continuous_rates = None
  best_continuous_rates_total = None

  # Loop through our rates and try and find the block of time that meets our desired
  # hours and has the lowest combined rates
  for index, rate in enumerate(applicable_rates):
    continuous_rates = [rate]
    continuous_rates_total = __get_intensity(rate)
    
    for offset in range(1, total_required_rates):
      if (index + offset) < applicable_rates_count:
        offset_rate = applicable_rates[(index + offset)]
        continuous_rates.append(offset_rate)
        continuous_rates_total += __get_intensity(offset_rate)
      else:
        break
    
    if ((best_continuous_rates == None or continuous_rates_total < best_continuous_rates_total) and len(continuous_rates) == total_required_rates):
      best_continuous_rates = continuous_rates
      best_continuous_rates_total = continuous_rates_total

  if best_continuous_rates is not None:
    # Make sure our rates are in ascending order before returning
    best_continuous_rates.sort(key=__get_to)
    return best_continuous_rates
  
  return []

def calculate_intermittent_times(current_date: datetime, target_start_time: str, target_end_time: str, target_hours: float, rates, is_rolling_target = True):
  applicable_rates = __get_applicable_rates(current_date, target_start_time, target_end_time, rates, is_rolling_target)
  if (applicable_rates is None):
    return []
  
  total_required_rates = math.ceil(target_hours * 2)

  applicable_rates.sort(key=__get_intensity)
  applicable_rates = applicable_rates[:total_required_rates]
  
  if (len(applicable_rates) < total_required_rates):
    return []

  # Make sure our rates are in ascending order before returning
  applicable_rates.sort(key=__get_to)
  return applicable_rates

def is_target_rate_active(current_date, applicable_rates, offset = None):
  is_active = False
  next_time = None
  total_applicable_rates = len(applicable_rates)

  if (total_applicable_rates > 0):
    if (current_date < applicable_rates[0]["from"]):
      next_time = applicable_rates[0]["from"]

    for index, rate in enumerate(applicable_rates):
      if (offset != None):
        valid_from = apply_offset(rate["from"], offset)
        valid_to = apply_offset(rate["to"], offset)
      else:
        valid_from = rate["from"]
        valid_to = rate["to"]

      if current_date >= valid_from and current_date < valid_to:
        is_active = True

        next_index = index + 1
        if (next_index < total_applicable_rates):
          next_time = applicable_rates[next_index]["from"]
        
        break

  return {
    "next_time": next_time,
    "is_active": is_active,
  }
