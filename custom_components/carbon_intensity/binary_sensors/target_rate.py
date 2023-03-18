import logging

import voluptuous as vol

from homeassistant.core import callback
from homeassistant.util.dt import (utcnow, now)
from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity
)
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
)
from ..const import (
  CONFIG_TARGET_OFFSET,

  CONFIG_TARGET_NAME,
  CONFIG_TARGET_HOURS,
  CONFIG_TARGET_TYPE,
  CONFIG_TARGET_START_TIME,
  CONFIG_TARGET_END_TIME,
  CONFIG_TARGET_ROLLING_TARGET,
  REGEX_HOURS,
  REGEX_OFFSET_PARTS,
  REGEX_TIME,
)

from ..utils import apply_offset

from . import (
  calculate_continuous_times,
  calculate_intermittent_times,
  is_target_rate_active
)

_LOGGER = logging.getLogger(__name__)

class CarbonIntensityTargetRate(CoordinatorEntity, BinarySensorEntity):
  """Sensor for calculating when a target should be turned on or off."""

  def __init__(self, coordinator, config):
    """Init sensor."""
    # Pass coordinator to base class
    super().__init__(coordinator)

    self._config = config
    self._attributes = self._config.copy()
    self._target_rates = []

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"carbon_intensity_target_{self._config[CONFIG_TARGET_NAME]}"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Carbon Intensity Target {self._config[CONFIG_TARGET_NAME]}"

  @property
  def icon(self):
    """Icon of the sensor."""
    return "mdi:camera-timer"

  @property
  def extra_state_attributes(self):
    """Attributes of the sensor."""
    return self._attributes

  @property
  def is_on(self):
    """The state of the sensor."""

    if CONFIG_TARGET_OFFSET in self._config:
      offset = self._config[CONFIG_TARGET_OFFSET]
    else:
      offset = None

    target_hours = float(self._config[CONFIG_TARGET_HOURS])

    # Find the current rate. Rates change a maximum of once every 30 minutes.
    current_date = utcnow()
    if (current_date.minute % 30) == 0 or len(self._target_rates) == 0:
      _LOGGER.info(f'Updating CarbonIntensityTargetRate {self._config[CONFIG_TARGET_NAME]}')

      # If all of our target times have passed, it's time to recalculate the next set
      all_rates_in_past = True
      for rate in self._target_rates:
        if rate["to"] > current_date:
          all_rates_in_past = False
          break
      
      if all_rates_in_past:
        all_rates = self.coordinator.data

        start_time = None
        if CONFIG_TARGET_START_TIME in self._config:
          start_time = self._config[CONFIG_TARGET_START_TIME]

        end_time = None
        if CONFIG_TARGET_END_TIME in self._config:
          end_time = self._config[CONFIG_TARGET_END_TIME]

        # True by default for backwards compatibility
        is_rolling_target = True
        if CONFIG_TARGET_ROLLING_TARGET in self._config:
          is_rolling_target = self._config[CONFIG_TARGET_ROLLING_TARGET]

        if (self._config[CONFIG_TARGET_TYPE] == "Continuous"):
          self._target_rates = calculate_continuous_times(
            now(),
            start_time,
            end_time,
            target_hours,
            all_rates,
            offset,
            is_rolling_target
          )
        elif (self._config[CONFIG_TARGET_TYPE] == "Intermittent"):
          self._target_rates = calculate_intermittent_times(
            now(),
            start_time,
            end_time,
            target_hours,
            all_rates,
            offset,
            is_rolling_target
          )
        else:
          _LOGGER.error(f"Unexpected target type: {self._config[CONFIG_TARGET_TYPE]}")

        self._attributes["target_times"] = self._target_rates

    active_result = is_target_rate_active(current_date, self._target_rates, offset)
    self._attributes["next_time"] = active_result["next_time"]

    return active_result["is_active"]
  
  async def async_added_to_hass(self):
    """Call when entity about to be added to hass."""
    # If not None, we got an initial value.
    await super().async_added_to_hass()
    state = await self.async_get_last_state()
    
    if state is not None and self._state is None:
      self._state = state.state
      self._attributes = {}
      for x in state.attributes.keys():
        self._attributes[x] = state.attributes[x]
    
      _LOGGER.debug(f'Restored CarbonIntensityTargetRate state: {self._state}')

  @callback
  def async_update_config(self, target_start_time=None, target_end_time=None, target_hours=None, target_offset=None):
    """Update sensors config"""

    config = dict(self._config)
    
    if target_hours is not None:
      # Inputs from automations can include quotes, so remove these
      trimmed_target_hours = target_hours.strip('\"')
      matches = re.search(REGEX_HOURS, trimmed_target_hours)
      if matches == None:
        raise vol.Invalid(f"Target hours of '{trimmed_target_hours}' must be in half hour increments.")
      else:
        trimmed_target_hours = float(trimmed_target_hours)
        if trimmed_target_hours % 0.5 != 0:
          raise vol.Invalid(f"Target hours of '{trimmed_target_hours}' must be in half hour increments.")
        else:
          config.update({
            CONFIG_TARGET_HOURS: trimmed_target_hours
          })

    if target_start_time is not None:
      # Inputs from automations can include quotes, so remove these
      trimmed_target_start_time = target_start_time.strip('\"')
      matches = re.search(REGEX_TIME, trimmed_target_start_time)
      if matches == None:
        raise vol.Invalid("Start time must be in the format HH:MM")
      else:
        config.update({
          CONFIG_TARGET_START_TIME: trimmed_target_start_time
        })

    if target_end_time is not None:
      # Inputs from automations can include quotes, so remove these
      trimmed_target_end_time = target_end_time.strip('\"')
      matches = re.search(REGEX_TIME, trimmed_target_end_time)
      if matches == None:
        raise vol.Invalid("End time must be in the format HH:MM")
      else:
        config.update({
          CONFIG_TARGET_END_TIME: trimmed_target_end_time
        })

    if target_offset is not None:
      # Inputs from automations can include quotes, so remove these
      trimmed_target_offset = target_offset.strip('\"')
      matches = re.search(REGEX_OFFSET_PARTS, trimmed_target_offset)
      if matches == None:
        raise vol.Invalid("Offset must be in the form of HH:MM:SS with an optional negative symbol")
      else:
        config.update({
          CONFIG_TARGET_OFFSET: trimmed_target_offset
        })

    self._config = config
    self._attributes = self._config.copy()
    self._target_rates = []
    self.async_write_ha_state()