import logging
from ..utils import apply_offset

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
)

from ..target_sensor_utils import (
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

    if offset != None and active_result["next_time"] != None:
      self._attributes["next_time"] = apply_offset(active_result["next_time"], offset)
    else:
      self._attributes["next_time"] = active_result["next_time"]

    return active_result["is_active"]