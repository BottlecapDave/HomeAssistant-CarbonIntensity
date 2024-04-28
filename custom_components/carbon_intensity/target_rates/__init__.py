from datetime import datetime, timedelta
import math
import re
import logging

from homeassistant.util.dt import (as_utc, parse_datetime)

from ..const import REGEX_OFFSET_PARTS

_LOGGER = logging.getLogger(__name__)

def apply_offset(date_time: datetime, offset: str, inverse = False):
  matches = re.search(REGEX_OFFSET_PARTS, offset)
  if matches == None:
    raise Exception(f'Unable to extract offset: {offset}')

  symbol = matches[1]
  hours = float(matches[2])
  minutes = float(matches[3])
  seconds = float(matches[4])

  if ((symbol == "-" and inverse == False) or (symbol != "-" and inverse == True)):
    return date_time - timedelta(hours=hours, minutes=minutes, seconds=seconds)
  
  return date_time + timedelta(hours=hours, minutes=minutes, seconds=seconds)

def get_applicable_rates(current_date: datetime, target_start_time: str, target_end_time: str, rates, is_rolling_target = True):
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
  if rates is not None:
    for rate in rates:
      if rate["from"] >= target_start and (target_end is None or rate["to"] <= target_end):
        new_rate = dict(rate)
        applicable_rates.append(new_rate)

  # Make sure that we have enough rates that meet our target period
  date_diff = target_end - target_start
  hours = (date_diff.days * 24) + (date_diff.seconds // 3600)
  periods = hours * 2
  if len(applicable_rates) < periods:
    _LOGGER.debug(f'Incorrect number of periods discovered. Require {periods}, but only have {len(applicable_rates)}')
    return None

  return applicable_rates

def __get_to(rate):
  return rate["to"]

def calculate_continuous_times(
    applicable_rates: list,
    target_hours: float,
    find_last_rates = False,
    max_intensity = None
  ):
  if (applicable_rates is None):
    return []
  
  applicable_rates.sort(key=__get_to, reverse=find_last_rates)
  applicable_rates_count = len(applicable_rates)
  total_required_rates = math.ceil(target_hours * 2)

  best_continuous_rates = None
  best_continuous_rates_total = None

  _LOGGER.debug(f'{applicable_rates_count} applicable rates found')

  # Loop through our rates and try and find the block of time that meets our desired
  # hours and has the lowest combined rates
  for index, rate in enumerate(applicable_rates):
    if (max_intensity is not None and rate["intensity_forecast"] > max_intensity):
      continue

    continuous_rates = [rate]
    continuous_rates_total = rate["intensity_forecast"]
    
    for offset in range(1, total_required_rates):
      if (index + offset) < applicable_rates_count:
        offset_rate = applicable_rates[(index + offset)]

        if (max_intensity is not None and offset_rate["intensity_forecast"] > max_intensity):
          break

        continuous_rates.append(offset_rate)
        continuous_rates_total += offset_rate["intensity_forecast"]
      else:
        break
    
    if ((best_continuous_rates is None or (continuous_rates_total < best_continuous_rates_total)) and len(continuous_rates) == total_required_rates):
      best_continuous_rates = continuous_rates
      best_continuous_rates_total = continuous_rates_total
    else:
      _LOGGER.debug(f'Total rates for current block {continuous_rates_total}. Total rates for best block {best_continuous_rates_total}')

  if best_continuous_rates is not None:
    # Make sure our rates are in ascending order before returning
    best_continuous_rates.sort(key=__get_to)
    return best_continuous_rates
  
  return []

def calculate_intermittent_times(
    applicable_rates: list,
    target_hours: float,
    find_last_rates = False,
    max_intensity = None
  ):
  if (applicable_rates is None):
    return []
  
  total_required_rates = math.ceil(target_hours * 2)

  if find_last_rates:
    applicable_rates.sort(key= lambda rate: (rate["intensity_forecast"], -rate["to"].timestamp()))
  else:
    applicable_rates.sort(key= lambda rate: (rate["intensity_forecast"], rate["to"]))

  applicable_rates = list(filter(lambda rate: (max_intensity is None or rate["intensity_forecast"] <= max_intensity), applicable_rates))
  applicable_rates = applicable_rates[:total_required_rates]
  
  _LOGGER.debug(f'{len(applicable_rates)} applicable rates found')
  
  if (len(applicable_rates) < total_required_rates):
    return []

  # Make sure our rates are in ascending order before returning
  applicable_rates.sort(key=__get_to)
  return applicable_rates

def get_target_rate_info(current_date: datetime, applicable_rates, offset: str = None):
  is_active = False
  next_time = None
  current_duration_in_hours = 0
  next_duration_in_hours = 0
  total_applicable_rates = len(applicable_rates)

  overall_total_cost = 0
  overall_min_intensity = None
  overall_max_intensity = None

  current_average_intensity = None
  current_min_intensity = None
  current_max_intensity = None

  next_average_intensity = None
  next_min_intensity = None
  next_max_intensity = None

  if (total_applicable_rates > 0):

    # Find the applicable rates that when combine become a continuous block. This is more for
    # intermittent rates.
    applicable_rates.sort(key=__get_to)
    applicable_rate_blocks = list()
    block_valid_from = applicable_rates[0]["from"]

    total_cost = 0
    min_intensity = None
    max_intensity = None

    for index, rate in enumerate(applicable_rates):
      if (index > 0 and applicable_rates[index - 1]["to"] != rate["from"]):
        diff = applicable_rates[index - 1]["to"] - block_valid_from
        minutes = diff.total_seconds() / 60
        applicable_rate_blocks.append({
          "from": block_valid_from,
          "to": applicable_rates[index - 1]["to"],
          "duration_in_hours": minutes / 60,
          "average_intensity": total_cost / (minutes / 30),
          "min_intensity": min_intensity,
          "max_intensity": max_intensity
        })

        block_valid_from = rate["from"]
        total_cost = 0
        min_intensity = None
        max_intensity = None

      total_cost += rate["intensity_forecast"]
      if min_intensity is None or min_intensity > rate["intensity_forecast"]:
        min_intensity = rate["intensity_forecast"]

      if max_intensity is None or max_intensity < rate["intensity_forecast"]:
        max_intensity = rate["intensity_forecast"]

      overall_total_cost += rate["intensity_forecast"]
      if overall_min_intensity is None or overall_min_intensity > rate["intensity_forecast"]:
        overall_min_intensity = rate["intensity_forecast"]

      if overall_max_intensity is None or overall_max_intensity < rate["intensity_forecast"]:
        overall_max_intensity = rate["intensity_forecast"]

    # Make sure our final block is added
    diff = applicable_rates[-1]["to"] - block_valid_from
    minutes = diff.total_seconds() / 60
    applicable_rate_blocks.append({
      "from": block_valid_from,
      "to": applicable_rates[-1]["to"],
      "duration_in_hours": minutes / 60,
      "average_intensity": total_cost / (minutes / 30),
      "min_intensity": min_intensity,
      "max_intensity": max_intensity
    })

    # Find out if we're within an active block, or find the next block
    for index, rate in enumerate(applicable_rate_blocks):
      if (offset is not None):
        valid_from = apply_offset(rate["from"], offset)
        valid_to = apply_offset(rate["to"], offset)
      else:
        valid_from = rate["from"]
        valid_to = rate["to"]
      
      if current_date >= valid_from and current_date < valid_to:
        current_duration_in_hours = rate["duration_in_hours"]
        current_average_intensity = rate["average_intensity"]
        current_min_intensity = rate["min_intensity"]
        current_max_intensity = rate["max_intensity"]
        is_active = True
      elif current_date < valid_from:
        next_time = valid_from
        next_duration_in_hours = rate["duration_in_hours"]
        next_average_intensity = rate["average_intensity"]
        next_min_intensity = rate["min_intensity"]
        next_max_intensity = rate["max_intensity"]
        break

  return {
    "is_active": is_active,
    "overall_average_intensity": round(overall_total_cost / total_applicable_rates, 5) if total_applicable_rates > 0  else 0,
    "overall_min_intensity": overall_min_intensity,
    "overall_max_intensity": overall_max_intensity,
    "current_duration_in_hours": current_duration_in_hours,
    "current_average_intensity": current_average_intensity,
    "current_min_intensity": current_min_intensity,
    "current_max_intensity": current_max_intensity,
    "next_time": next_time,
    "next_duration_in_hours": next_duration_in_hours,
    "next_average_intensity": next_average_intensity,
    "next_min_intensity": next_min_intensity,
    "next_max_intensity": next_max_intensity,
  }