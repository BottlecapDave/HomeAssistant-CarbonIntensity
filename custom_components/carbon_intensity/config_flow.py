import re
import voluptuous as vol
import logging

from homeassistant.config_entries import (ConfigFlow, OptionsFlow)
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
  DOMAIN,
  
  CONFIG_MAIN_REGION,
  
  CONFIG_TARGET_NAME,
  CONFIG_TARGET_HOURS,
  CONFIG_TARGET_START_TIME,
  CONFIG_TARGET_END_TIME,
  CONFIG_TARGET_TYPE,
  CONFIG_TARGET_OFFSET,
  CONFIG_TARGET_ROLLING_TARGET,
  CONFIG_TARGET_LAST_RATES,
  CONFIG_TARGET_MAX_RATE
)

from .config.target_rates import validate_target_rate_config
from .utils import get_region_options

_LOGGER = logging.getLogger(__name__)

class CarbonIntensityConfigFlow(ConfigFlow, domain=DOMAIN): 
  """Config flow."""

  VERSION = 1

  async def __async_setup_settings_schema(self):
    regions = get_region_options()

    return vol.Schema({
      vol.Required(CONFIG_MAIN_REGION): vol.In(regions),
    })

  async def __async_setup_target_rate_schema(self):
    return vol.Schema({
      vol.Required(CONFIG_TARGET_NAME): str,
      vol.Required(CONFIG_TARGET_HOURS): str,
      vol.Required(CONFIG_TARGET_TYPE, default="Continuous"): vol.In({
        "Continuous": "Continuous",
        "Intermittent": "Intermittent"
      }),
      vol.Optional(CONFIG_TARGET_START_TIME): str,
      vol.Optional(CONFIG_TARGET_END_TIME): str,
      vol.Optional(CONFIG_TARGET_OFFSET): str,
      vol.Optional(CONFIG_TARGET_ROLLING_TARGET, default=False): bool,
      vol.Optional(CONFIG_TARGET_LAST_RATES): bool,
      vol.Optional(CONFIG_TARGET_MAX_RATE): float,
    })

  async def async_step_target_rate(self, user_input):
    """Setup a target based on the provided user input"""
    
    errors = validate_target_rate_config(user_input)

    if len(errors) < 1:
      # Setup our targets sensor
      return self.async_create_entry(
        title=f"{user_input[CONFIG_TARGET_NAME]} (target)", 
        data=user_input
      )

    # Reshow our form with raised errors
    data_Schema = await self.__async_setup_target_rate_schema()
    return self.async_show_form(
      step_id="target_rate", data_schema=data_Schema, errors=errors
    )

  async def async_step_user(self, user_input):
    """Setup based on user config"""

    is_settings_setup = False
    for entry in self._async_current_entries(include_ignore=False):
      if CONFIG_MAIN_REGION in entry.data:
        is_settings_setup = True
        break

    if user_input is not None:
      # We are setting up our initial stage
      if CONFIG_MAIN_REGION in user_input:
        return self.async_create_entry(
        title="Carbon Intensity", 
        data=user_input
      )

      # We are setting up a target
      if CONFIG_TARGET_NAME in user_input:
        return await self.async_step_target_rate(user_input)

    if is_settings_setup:
      data_Schema = await self.__async_setup_target_rate_schema()
      return self.async_show_form(
        step_id="target_rate", data_schema=data_Schema
      )

    data_Schema = await self.__async_setup_settings_schema()
    return self.async_show_form(
      step_id="user", data_schema=data_Schema
    )

  @staticmethod
  @callback
  def async_get_options_flow(entry):
    return OptionsFlowHandler(entry)

class OptionsFlowHandler(OptionsFlow):
  """Handles options flow for the component."""

  def __init__(self, entry) -> None:
    self._entry = entry

  async def __async_setup_target_rate_schema(self, config, errors):
    start_time_key = vol.Optional(CONFIG_TARGET_START_TIME)
    if (CONFIG_TARGET_START_TIME in config):
      start_time_key = vol.Optional(CONFIG_TARGET_START_TIME, default=config[CONFIG_TARGET_START_TIME])

    end_time_key = vol.Optional(CONFIG_TARGET_END_TIME)
    if (CONFIG_TARGET_END_TIME in config):
      end_time_key = vol.Optional(CONFIG_TARGET_END_TIME, default=config[CONFIG_TARGET_END_TIME])

    offset_key = vol.Optional(CONFIG_TARGET_OFFSET)
    if (CONFIG_TARGET_OFFSET in config):
      offset_key = vol.Optional(CONFIG_TARGET_OFFSET, default=config[CONFIG_TARGET_OFFSET])

    # True by default for backwards compatibility
    is_rolling_target = True
    if (CONFIG_TARGET_ROLLING_TARGET in config):
      is_rolling_target = config[CONFIG_TARGET_ROLLING_TARGET]

    find_last_rates = False
    if (CONFIG_TARGET_LAST_RATES in config):
      find_last_rates = config[CONFIG_TARGET_LAST_RATES]
    
    return self.async_show_form(
      step_id="target_rate",
      data_schema=self.add_suggested_values_to_schema(
          vol.Schema({
            vol.Required(CONFIG_TARGET_NAME): str,
            vol.Required(CONFIG_TARGET_HOURS): str,
            vol.Required(CONFIG_TARGET_TYPE, default="Continuous"): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[
                      selector.SelectOptionDict(value="Continuous", label="Continuous"),
                      selector.SelectOptionDict(value="Intermittent", label="Intermittent"),
                    ],
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
            start_time_key: str,
            end_time_key: str,
            offset_key: str,
            vol.Optional(CONFIG_TARGET_ROLLING_TARGET): bool,
            vol.Optional(CONFIG_TARGET_LAST_RATES): bool,
            vol.Optional(CONFIG_TARGET_MAX_RATE): float,
          }),
          {
            CONFIG_TARGET_NAME: config[CONFIG_TARGET_NAME],
            CONFIG_TARGET_HOURS: f'{config[CONFIG_TARGET_HOURS]}',
            CONFIG_TARGET_TYPE: config[CONFIG_TARGET_TYPE],
            CONFIG_TARGET_ROLLING_TARGET: is_rolling_target,
            CONFIG_TARGET_LAST_RATES: find_last_rates,
            CONFIG_TARGET_MAX_RATE: config[CONFIG_TARGET_MAX_RATE] if CONFIG_TARGET_MAX_RATE in config else None
          }
      ),
      errors=errors
    )

  async def __async_setup_settings_schema(self, config):
    regions = get_region_options()
      
    return self.async_show_form(
      step_id="user", data_schema=vol.Schema({
        vol.Required(CONFIG_MAIN_REGION, default=config[CONFIG_MAIN_REGION]): vol.In(regions),
      })
    )

  async def async_step_init(self, user_input):
    """Manage the options for the custom component."""

    config = dict(self._entry.data)
    if self._entry.options is not None:
      config.update(self._entry.options)

    if CONFIG_MAIN_REGION in self._entry.data:
      return await self.__async_setup_settings_schema(config)
    elif CONFIG_TARGET_TYPE in self._entry.data:
      return await self.__async_setup_target_rate_schema(config, {})

    return self.async_abort(reason="not_supported")

  async def async_step_user(self, user_input):
    """Manage the options for the custom component."""

    if user_input is not None:
      config = dict(self._entry.data)
      config.update(user_input)
      return self.async_create_entry(title="", data=config)

    return self.async_abort(reason="not_supported")

  async def async_step_target_rate(self, user_input):
    """Manage the options for the custom component."""

    if user_input is not None:
      config = dict(self._entry.data)
      config.update(user_input)

      errors = validate_target_rate_config(config)

      if (len(errors) > 0):
        return await self.__async_setup_target_rate_schema(config, errors)

      return self.async_create_entry(title="", data=config)

    return self.async_abort(reason="not_supported")