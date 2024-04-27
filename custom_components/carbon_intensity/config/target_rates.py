import re
from datetime import timedelta

from homeassistant.util.dt import (parse_datetime)

from ..const import (
  CONFIG_TARGET_END_TIME,
  CONFIG_TARGET_HOURS,
  CONFIG_TARGET_MAX_RATE,
  CONFIG_TARGET_NAME,
  CONFIG_TARGET_OFFSET,
  CONFIG_TARGET_START_TIME,
  REGEX_ENTITY_NAME,
  REGEX_HOURS,
  REGEX_OFFSET_PARTS,
  REGEX_PRICE,
  REGEX_TIME
)

def merge_target_rate_config(data: dict, options: dict, updated_config: dict = None):
  config = dict(data)
  if options is not None:
    config.update(options)

  if updated_config is not None:
    config.update(updated_config)

    if CONFIG_TARGET_START_TIME not in updated_config and CONFIG_TARGET_START_TIME in config:
      config[CONFIG_TARGET_START_TIME] = None

    if CONFIG_TARGET_END_TIME not in updated_config and CONFIG_TARGET_END_TIME in config:
      config[CONFIG_TARGET_END_TIME] = None

    if CONFIG_TARGET_OFFSET not in updated_config and CONFIG_TARGET_OFFSET in config:
      config[CONFIG_TARGET_OFFSET] = None

    if CONFIG_TARGET_MAX_RATE not in updated_config and CONFIG_TARGET_MAX_RATE in config:
      config[CONFIG_TARGET_MAX_RATE] = None

  return config

def is_time_frame_long_enough(hours, start_time, end_time):
  start_time = parse_datetime(f"2023-08-01T{start_time}:00Z")
  end_time = parse_datetime(f"2023-08-01T{end_time}:00Z")
  if end_time <= start_time:
    end_time = end_time + timedelta(days=1)

  time_diff = end_time - start_time
  available_minutes = time_diff.total_seconds() / 60
  target_minutes = (hours / 0.5) * 30

  return available_minutes >= target_minutes

def validate_target_rate_config(data):
  errors = {}

  matches = re.search(REGEX_ENTITY_NAME, data[CONFIG_TARGET_NAME])
  if matches is None:
    errors[CONFIG_TARGET_NAME] = "invalid_target_name"

  # For some reason float type isn't working properly - reporting user input malformed
  if isinstance(data[CONFIG_TARGET_HOURS], float) == False:
    matches = re.search(REGEX_HOURS, data[CONFIG_TARGET_HOURS])
    if matches is None:
      errors[CONFIG_TARGET_HOURS] = "invalid_target_hours"
    else:
      data[CONFIG_TARGET_HOURS] = float(data[CONFIG_TARGET_HOURS])
  
  if CONFIG_TARGET_HOURS not in errors:
    if data[CONFIG_TARGET_HOURS] % 0.5 != 0:
      errors[CONFIG_TARGET_HOURS] = "invalid_target_hours"

  if CONFIG_TARGET_START_TIME in data:
    matches = re.search(REGEX_TIME, data[CONFIG_TARGET_START_TIME])
    if matches is None:
      errors[CONFIG_TARGET_START_TIME] = "invalid_target_time"

  if CONFIG_TARGET_END_TIME in data:
    matches = re.search(REGEX_TIME, data[CONFIG_TARGET_END_TIME])
    if matches is None:
      errors[CONFIG_TARGET_END_TIME] = "invalid_target_time"

  if CONFIG_TARGET_OFFSET in data:
    matches = re.search(REGEX_OFFSET_PARTS, data[CONFIG_TARGET_OFFSET])
    if matches is None:
      errors[CONFIG_TARGET_OFFSET] = "invalid_offset"

  if CONFIG_TARGET_MAX_RATE in data and data[CONFIG_TARGET_MAX_RATE] is not None:
    if isinstance(data[CONFIG_TARGET_MAX_RATE], float) == False:
      matches = re.search(REGEX_PRICE, data[CONFIG_TARGET_MAX_RATE])
      if matches is None:
        errors[CONFIG_TARGET_MAX_RATE] = "invalid_intensity"
      else:
        data[CONFIG_TARGET_MAX_RATE] = float(data[CONFIG_TARGET_MAX_RATE])

  start_time = data[CONFIG_TARGET_START_TIME] if CONFIG_TARGET_START_TIME in data else "00:00"
  end_time = data[CONFIG_TARGET_END_TIME] if CONFIG_TARGET_END_TIME in data else "00:00"

  is_time_valid = CONFIG_TARGET_START_TIME not in errors and CONFIG_TARGET_END_TIME not in errors

  if CONFIG_TARGET_HOURS not in errors and is_time_valid:
    if is_time_frame_long_enough(data[CONFIG_TARGET_HOURS], start_time, end_time) == False:
      errors[CONFIG_TARGET_HOURS] = "invalid_hours_time_frame"

  return errors