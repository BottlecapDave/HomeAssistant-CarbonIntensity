import voluptuous as vol
import logging

from homeassistant.config_entries import (ConfigFlow, OptionsFlow)
from homeassistant.core import callback

from .const import (
  DOMAIN,
  
  CONFIG_MAIN_REGION
)

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

  async def async_step_user(self, user_input):
    """Setup based on user config"""

    if user_input is not None:
      # We are setting up our initial stage
      if CONFIG_MAIN_REGION in user_input:
        return self.async_create_entry(
        title="Carbon Intensity", 
        data=user_input
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

    return self.async_abort(reason="not_supported")

  async def async_step_user(self, user_input):
    """Manage the options for the custom component."""

    if user_input is not None:
      config = dict(self._entry.data)
      config.update(user_input)
      return self.async_create_entry(title="", data=config)

    return self.async_abort(reason="not_supported")