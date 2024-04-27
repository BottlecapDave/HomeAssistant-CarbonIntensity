import logging

from homeassistant.core import HomeAssistant, callback
from homeassistant.util.dt import (utcnow)
from homeassistant.helpers.entity import generate_entity_id
from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity
)
from homeassistant.components.sensor import (
    RestoreSensor,
)

from ..entities import get_current_rate
from ..utils import get_region_for_unique_id_from_id, get_region_from_id
from ..utils.attributes import dict_to_typed_dict

_LOGGER = logging.getLogger(__name__)

class CarbonIntensityCurrentRating(CoordinatorEntity, RestoreSensor):
  """Sensor for displaying the current rate."""

  def __init__(self, hass: HomeAssistant, coordinator, region: str):
    """Init sensor."""
    CoordinatorEntity.__init__(self, coordinator)

    self._state = None
    self._region = region

    self.entity_id = generate_entity_id("sensor.{}", self.unique_id, hass=hass)

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"carbon_intensity_{get_region_for_unique_id_from_id(self._region)}_current_rating"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Current Rating ({get_region_from_id(self._region)})"

  @property
  def icon(self):
    """Icon of the sensor."""
    return "mdi:leaf"

  @property
  def extra_state_attributes(self):
    """Attributes of the sensor."""
    return self._attributes

  @property
  def unit_of_measurement(self):
    """Unit of measurement of the sensor."""
    return "gCO2/kWh"

  @property
  def state(self):
    """The state of the sensor."""
    return self._state
  
  @callback
  def _handle_coordinator_update(self) -> None:
    # Find the current rate. We only need to do this every half an hour
    now = utcnow()
    self._state = None
    self._attributes = {}
    
    _LOGGER.info(f"Updating CarbonIntensityCurrentRating")

    rates = self.coordinator.data.rates if self.coordinator is not None and self.coordinator.data is not None else None

    current_rate = get_current_rate(now, rates)
    self._attributes = {
      "rate": current_rate
    }

    if current_rate is not None:
      self._state = current_rate["intensity_forecast"]
    
    self._attributes = dict_to_typed_dict(self._attributes)
    super()._handle_coordinator_update()

  async def async_added_to_hass(self):
    """Call when entity about to be added to hass."""
    # If not None, we got an initial value.
    await super().async_added_to_hass()
    state = await self.async_get_last_state()
    
    if state is not None and self._state is None:
      self._state = state.state
      self._attributes = {}
      for x in state.attributes.keys():
        if x != "all_rates":
          self._attributes[x] = state.attributes[x]

      self._attributes = dict_to_typed_dict(self._attributes)
    
      _LOGGER.debug(f'Restored CarbonIntensityCurrentRating state: {self._state}')