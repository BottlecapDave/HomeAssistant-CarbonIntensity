import logging

from homeassistant.util.dt import (utcnow)
from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity
)
from homeassistant.components.sensor import (
    SensorEntity,
)

_LOGGER = logging.getLogger(__name__)

class CarbonIntensityCurrentRating(CoordinatorEntity, SensorEntity):
  """Sensor for displaying the current rate."""

  def __init__(self, coordinator):
    """Init sensor."""
    # Pass coordinator to base class
    super().__init__(coordinator)

    self._state = None

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"carbon_intensity_current_rating"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Carbon Intensity Current Rating"

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
    # Find the current rate. We only need to do this every half an hour
    now = utcnow()
    self._state = None
    self._attributes = {}
    
    _LOGGER.info(f"Updating CarbonIntensityCurrentRating")

    current_rate = None
    if self.coordinator.data != None:
      for period in self.coordinator.data:
        if now >= period["from"] and now <= period["to"]:
          current_rate = period
          break

    if current_rate != None:
      self._attributes = {
        "rate": current_rate,
        "all_rates": self.coordinator.data
      }
      
      if current_rate != None:
        self._state = current_rate["intensity_forecast"]

    return self._state