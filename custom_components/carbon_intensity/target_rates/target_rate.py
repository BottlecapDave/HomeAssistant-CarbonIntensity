import logging

import voluptuous as vol

from homeassistant.const import (
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)

from homeassistant.core import HomeAssistant, callback
from homeassistant.util.dt import (utcnow, now)
from homeassistant.helpers.entity import generate_entity_id
from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity
)
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
)
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers import translation

from ..const import (
  CONFIG_TARGET_LAST_RATES,
  CONFIG_TARGET_MAX_RATE,
  CONFIG_TARGET_OFFSET,

  CONFIG_TARGET_NAME,
  CONFIG_TARGET_HOURS,
  CONFIG_TARGET_TYPE,
  CONFIG_TARGET_START_TIME,
  CONFIG_TARGET_END_TIME,
  CONFIG_TARGET_ROLLING_TARGET,
  DOMAIN,
)

from . import (
  calculate_continuous_times,
  calculate_intermittent_times,
  get_applicable_rates,
  get_target_rate_info
)
  
from ..config.target_rates import validate_target_rate_config
from ..utils.attributes import dict_to_typed_dict

_LOGGER = logging.getLogger(__name__)

class CarbonIntensityTargetRate(CoordinatorEntity, BinarySensorEntity, RestoreEntity):
  """Sensor for calculating when a target should be turned on or off."""

  def __init__(self, hass: HomeAssistant, coordinator, config):
    """Init sensor."""
    # Pass coordinator to base class
    super().__init__(coordinator)

    self._state = None
    self._config = config
    self._attributes = self._config.copy()
    self._last_evaluated = None
    
    is_rolling_target = True
    if CONFIG_TARGET_ROLLING_TARGET in self._config:
      is_rolling_target = self._config[CONFIG_TARGET_ROLLING_TARGET]
    self._attributes[CONFIG_TARGET_ROLLING_TARGET] = is_rolling_target

    find_last_rates = False
    if CONFIG_TARGET_LAST_RATES in self._config:
      find_last_rates = self._config[CONFIG_TARGET_LAST_RATES]
    self._attributes[CONFIG_TARGET_LAST_RATES] = find_last_rates

    self._target_rates = []
    
    self._hass = hass
    self.entity_id = generate_entity_id("binary_sensor.{}", self.unique_id, hass=hass)

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
    return self._state
  
  @callback
  def _handle_coordinator_update(self) -> None:
    """Determines if the target rate sensor is active."""
    if CONFIG_TARGET_OFFSET in self._config:
      offset = self._config[CONFIG_TARGET_OFFSET]
    else:
      offset = None

    current_local_date = now()

    # Find the current rate. Rates change a maximum of once every 30 minutes.
    current_date = utcnow()

    _LOGGER.debug(f'Updating CarbonIntensityTargetRate {self._config[CONFIG_TARGET_NAME]}')
    self._last_evaluated = current_date

    # If all of our target times have passed, it's time to recalculate the next set
    all_rates_in_past = True
    for rate in self._target_rates:
      if rate["to"] > current_date:
        all_rates_in_past = False
        break
    
    if all_rates_in_past:
      if self.coordinator is not None and self.coordinator.data is not None:
        all_rates = self.coordinator.data.rates
      else:
        _LOGGER.debug(f"Rate data missing. Setting to empty array")
        all_rates = []

      _LOGGER.debug(f'{len(all_rates) if all_rates is not None else None} rate periods found')

      if len(all_rates) > 0:
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

        find_last_rates = False
        if CONFIG_TARGET_LAST_RATES in self._config:
          find_last_rates = self._config[CONFIG_TARGET_LAST_RATES]     

        target_hours = float(self._config[CONFIG_TARGET_HOURS])

        max_rate = None
        if CONFIG_TARGET_MAX_RATE in self._config:
          max_rate = self._config[CONFIG_TARGET_MAX_RATE]

        applicable_rates = get_applicable_rates(
          current_local_date,
          start_time,
          end_time,
          all_rates,
          is_rolling_target
        )

        if (self._config[CONFIG_TARGET_TYPE] == "Continuous"):
          self._target_rates = calculate_continuous_times(
            applicable_rates,
            target_hours,
            find_last_rates,
            max_rate
          )
        elif (self._config[CONFIG_TARGET_TYPE] == "Intermittent"):
          self._target_rates = calculate_intermittent_times(
            applicable_rates,
            target_hours,
            find_last_rates,
            max_rate
          )
        else:
          _LOGGER.error(f"Unexpected target type: {self._config[CONFIG_TARGET_TYPE]}")

        self._attributes["rates_incomplete"] = applicable_rates is None
        self._attributes["target_times"] = self._target_rates
        self._attributes["target_times_last_evaluated"] = current_date
        _LOGGER.debug(f"calculated rates: {self._target_rates}")

    active_result = get_target_rate_info(current_date, self._target_rates, offset)

    self._attributes["overall_average_intensity"] = active_result["overall_average_intensity"]
    self._attributes["overall_min_intensity"] = active_result["overall_min_intensity"]
    self._attributes["overall_max_intensity"] = active_result["overall_max_intensity"]

    self._attributes["current_duration_in_hours"] = active_result["current_duration_in_hours"]
    self._attributes["current_average_intensity"] = active_result["current_average_intensity"]
    self._attributes["current_min_intensity"] = active_result["current_min_intensity"]
    self._attributes["current_max_intensity"] = active_result["current_max_intensity"]

    self._attributes["next_time"] = active_result["next_time"]
    self._attributes["next_duration_in_hours"] = active_result["next_duration_in_hours"]
    self._attributes["next_average_intensity"] = active_result["next_average_intensity"]
    self._attributes["next_min_intensity"] = active_result["next_min_intensity"]
    self._attributes["next_max_intensity"] = active_result["next_max_intensity"]
    
    self._attributes["last_evaluated"] = current_date
    self._state = active_result["is_active"]

    _LOGGER.debug(f"calculated: {self._state}")
    self._attributes = dict_to_typed_dict(self._attributes)
    super()._handle_coordinator_update()

  async def async_added_to_hass(self):
    """Call when entity about to be added to hass."""
    # If not None, we got an initial value.
    await super().async_added_to_hass()
    state = await self.async_get_last_state()
    
    if state is not None and self._state is None:
      self._state = None if state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN) or state.state is None else state.state.lower() == 'on'
      self._attributes = dict_to_typed_dict(state.attributes)
      # Make sure our attributes don't override any changed settings
      self._attributes.update(self._config)
    
      _LOGGER.debug(f'Restored CarbonIntensityTargetRate state: {self._state}')  

  @callback
  async def async_update_config(self, target_start_time=None, target_end_time=None, target_hours=None, target_offset=None, target_maximum_intensity=None):
    """Update sensors config"""

    config = dict(self._config)
    if target_hours is not None:
      # Inputs from automations can include quotes, so remove these
      trimmed_target_hours = target_hours.strip('\"')
      config.update({
        CONFIG_TARGET_HOURS: trimmed_target_hours
      })

    if target_start_time is not None:
      # Inputs from automations can include quotes, so remove these
      trimmed_target_start_time = target_start_time.strip('\"')
      config.update({
        CONFIG_TARGET_START_TIME: trimmed_target_start_time
      })

    if target_end_time is not None:
      # Inputs from automations can include quotes, so remove these
      trimmed_target_end_time = target_end_time.strip('\"')
      config.update({
        CONFIG_TARGET_END_TIME: trimmed_target_end_time
      })

    if target_offset is not None:
      # Inputs from automations can include quotes, so remove these
      trimmed_target_offset = target_offset.strip('\"')
      config.update({
        CONFIG_TARGET_OFFSET: trimmed_target_offset
      })

    if target_maximum_intensity is not None:
      # Inputs from automations can include quotes, so remove these
      trimmed_target_maximum_intensity = target_maximum_intensity.strip('\"')
      config.update({
        CONFIG_TARGET_MAX_RATE: trimmed_target_maximum_intensity if trimmed_target_maximum_intensity != "" else None
      })

    errors = validate_target_rate_config(config)
    keys = list(errors.keys())
    if (len(keys)) > 0:
      translations = await translation.async_get_translations(self._hass, self._hass.config.language, "options", {DOMAIN})
      raise vol.Invalid(translations[f'component.{DOMAIN}.options.error.{errors[keys[0]]}'])

    self._config = config
    self._attributes = self._config.copy()
    self._target_rates = []
    self.async_write_ha_state()