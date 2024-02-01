import logging

from homeassistant.core import HomeAssistant, callback

from homeassistant.components.event import (
    EventEntity,
)
from homeassistant.helpers.restore_state import RestoreEntity

from ..const import EVENT_CURRENT_DAY_RATES
from ..utils import get_region_for_unique_id_from_id, get_region_from_id

_LOGGER = logging.getLogger(__name__)

class CarbonIntensityCurrentDayRates(EventEntity, RestoreEntity):
  """Sensor for displaying the current day's rates."""

  _entity_component_unrecorded_attributes = frozenset(
    {"rates"}
  )

  def __init__(self, hass: HomeAssistant, region):
    """Init sensor."""

    self._hass = hass
    self._region = region
    self._state = None
    self._last_updated = None

    self._attr_event_types = [EVENT_CURRENT_DAY_RATES]

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"carbon_intensity_{get_region_for_unique_id_from_id(self._region)}_current_day_rates"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Carbon Intensity {get_region_from_id(self._region)} Current Day Rates"
  
  @property
  def entity_registry_enabled_default(self) -> bool:
    """Return if the entity should be enabled when first added.

    This only applies when fist added to the entity registry.
    """
    return False

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
    
      _LOGGER.debug(f'Restored CarbonIntensityCurrentDayRates state: {self._state}')

  async def async_added_to_hass(self) -> None:
    """Register callbacks."""
    self._hass.bus.async_listen(self._attr_event_types[0], self._async_handle_event)

  @callback
  def _async_handle_event(self, event) -> None:
    if (event.data is not None and "region" in event.data and event.data["region"] == self._region):
      self._trigger_event(event.event_type, event.data)
      self.async_write_ha_state()