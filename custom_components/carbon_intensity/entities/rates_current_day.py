import logging

from homeassistant.core import HomeAssistant, callback

from homeassistant.components.event import (
    EventEntity,
    EventExtraStoredData,
)
from homeassistant.helpers.entity import generate_entity_id
from homeassistant.helpers.restore_state import RestoreEntity

from ..const import EVENT_CURRENT_DAY_RATES
from ..utils import get_region_for_unique_id_from_id, get_region_from_id
from ..utils.attributes import dict_to_typed_dict

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
    self.entity_id = generate_entity_id("event.{}", self.unique_id, hass=hass)

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"carbon_intensity_{get_region_for_unique_id_from_id(self._region)}_current_day_rates"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Current Day Rates ({get_region_from_id(self._region)})"
  
  @property
  def entity_registry_enabled_default(self) -> bool:
    """Return if the entity should be enabled when first added.

    This only applies when fist added to the entity registry.
    """
    return False

  async def async_get_last_event_data(self):
    data = await super().async_get_last_event_data()
    return EventExtraStoredData.from_dict({
      "last_event_type": data.last_event_type,
      "last_event_attributes": dict_to_typed_dict(data.last_event_attributes),
    })

  async def async_added_to_hass(self):
    """Call when entity about to be added to hass."""
    # If not None, we got an initial value.
    await super().async_added_to_hass()
    self._hass.bus.async_listen(self._attr_event_types[0], self._async_handle_event)

  @callback
  def _async_handle_event(self, event) -> None:
    _LOGGER.debug(f"region: {self._region}; data: {event.data}")
    if (event.data is not None and "region" in event.data and event.data["region"] == self._region):
      self._trigger_event(event.event_type, event.data)
      self.async_write_ha_state()