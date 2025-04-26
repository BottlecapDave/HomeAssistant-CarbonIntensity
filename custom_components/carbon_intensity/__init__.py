import logging

from .const import (
  DOMAIN,
  CONFIG_MAIN_REGION,
  DATA_CONFIG,
)
from .coordinators.rates import async_setup_rates_coordinator

ACCOUNT_PLATFORMS = ["sensor", "event"]

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry):
  """This is called from the config flow."""
  hass.data.setdefault(DOMAIN, {})

  if CONFIG_MAIN_REGION in entry.data:
    config = dict(entry.data)

    if entry.options:
      config.update(entry.options)

    await async_setup_dependencies(hass, config)

    await hass.config_entries.async_forward_entry_setups(entry, ACCOUNT_PLATFORMS)
  
  entry.async_on_unload(entry.add_update_listener(options_update_listener))

  return True

async def async_setup_dependencies(hass, config):
  """Setup the coordinator and api client which will be shared by various entities"""

  hass.data[DOMAIN][DATA_CONFIG] = config

  await async_setup_rates_coordinator(hass, config)

async def options_update_listener(hass, entry):
  """Handle options update."""
  await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass, entry):
    """Unload a config entry."""
    if CONFIG_MAIN_REGION in entry.data:
      unload_ok = await hass.config_entries.async_unload_platforms(entry, ACCOUNT_PLATFORMS)

    return unload_ok