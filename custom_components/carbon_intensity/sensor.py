# from datetime import timedelta
# import logging

# from homeassistant.util.dt import (utcnow, now, as_utc, parse_datetime)
# from homeassistant.helpers.update_coordinator import (
#   CoordinatorEntity,
#   DataUpdateCoordinator
# )
# from homeassistant.components.sensor import (
#     DEVICE_CLASS_MONETARY,
#     DEVICE_CLASS_ENERGY,
#     DEVICE_CLASS_GAS,
#     STATE_CLASS_TOTAL_INCREASING,
#     SensorEntity,
# )
# from homeassistant.const import (
#     ENERGY_KILO_WATT_HOUR,
#     VOLUME_CUBIC_METERS
# )

# from .sensor_utils import (
#   async_get_consumption_data,
#   calculate_electricity_consumption,
#   async_calculate_electricity_cost,
#   calculate_gas_consumption,
#   async_calculate_gas_cost
# )

# from .utils import (get_active_tariff_code)
# from .const import (
#   DOMAIN,
  
#   CONFIG_MAIN_API_KEY,
#   CONFIG_MAIN_ACCOUNT_ID,
  
#   CONFIG_SMETS1,

#   DATA_ELECTRICITY_RATES_COORDINATOR,
#   DATA_CLIENT
# )

# _LOGGER = logging.getLogger(__name__)

# SCAN_INTERVAL = timedelta(minutes=1)

# def create_reading_coordinator(hass, client, is_electricity, identifier, serial_number):
#   """Create reading coordinator"""

#   async def async_update_data():
#     """Fetch data from API endpoint."""

#     previous_consumption_key = f'{identifier}_{serial_number}_previous_consumption'
#     previous_data = None
#     if previous_consumption_key in hass.data[DOMAIN]:
#       previous_data = hass.data[DOMAIN][previous_consumption_key]

#     period_from = as_utc((now() - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0))
#     period_to = as_utc(now().replace(hour=0, minute=0, second=0, microsecond=0))

#     data = await async_get_consumption_data(
#       client,
#       previous_data,
#       utcnow(),
#       period_from,
#       period_to,
#       identifier,
#       serial_number,
#       is_electricity
#     )

#     if data != None and len(data) > 0:
#       hass.data[DOMAIN][previous_consumption_key] = data
#       return data

#     return []

#   coordinator = DataUpdateCoordinator(
#     hass,
#     _LOGGER,
#     name="rates",
#     update_method=async_update_data,
#     # Because of how we're using the data, we'll update every minute, but we will only actually retrieve
#     # data every 30 minutes
#     update_interval=timedelta(minutes=1),
#   )

#   hass.data[DOMAIN][f'{identifier}_{serial_number}_consumption_coordinator'] = coordinator

#   return coordinator

# async def async_setup_entry(hass, entry, async_add_entities):
#   """Setup sensors based on our entry"""

#   if CONFIG_MAIN_API_KEY in entry.data:
#     await async_setup_default_sensors(hass, entry, async_add_entities)

# async def async_setup_default_sensors(hass, entry, async_add_entities):
#   config = dict(entry.data)

#   if entry.options:
#     config.update(entry.options)

#   is_smets1 = False
#   if CONFIG_SMETS1 in config:
#     is_smets1 = config[CONFIG_SMETS1]
  
#   client = hass.data[DOMAIN][DATA_CLIENT]
  
#   rate_coordinator = hass.data[DOMAIN][DATA_ELECTRICITY_RATES_COORDINATOR]

#   await rate_coordinator.async_config_entry_first_refresh()

#   entities = []
  
#   account_info = await client.async_get_account(config[CONFIG_MAIN_ACCOUNT_ID])

#   now = utcnow()

#   if len(account_info["electricity_meter_points"]) > 0:
#     for point in account_info["electricity_meter_points"]:
#       # We only care about points that have active agreements
#       electricity_tariff_code = get_active_tariff_code(now, point["agreements"])
#       if electricity_tariff_code != None:
#         for meter in point["meters"]:
#           _LOGGER.info(f'Adding electricity meter; mpan: {point["mpan"]}; serial number: {meter["serial_number"]}')
#           coordinator = create_reading_coordinator(hass, client, True, point["mpan"], meter["serial_number"])
#           entities.append(OctopusEnergyPreviousAccumulativeElectricityReading(coordinator, point["mpan"], meter["serial_number"], point["is_export"]))
#           entities.append(OctopusEnergyPreviousAccumulativeElectricityCost(coordinator, client, electricity_tariff_code, point["mpan"], meter["serial_number"], point["is_export"]))
#           entities.append(OctopusEnergyElectricityCurrentRate(rate_coordinator, point["mpan"], meter["serial_number"], point["is_export"]))
#           entities.append(OctopusEnergyElectricityPreviousRate(rate_coordinator, point["mpan"], meter["serial_number"], point["is_export"]))
#       else:
#         for meter in point["meters"]:
#           _LOGGER.info(f'Skipping electricity meter due to no active agreement; mpan: {point["mpan"]}; serial number: {meter["serial_number"]}')
#         _LOGGER.info(f'agreements: {point["agreements"]}')
#   else:
#     _LOGGER.info('No electricity meters available')

#   if len(account_info["gas_meter_points"]) > 0:
#     for point in account_info["gas_meter_points"]:
#       # We only care about points that have active agreements
#       gas_tariff_code = get_active_tariff_code(now, point["agreements"])
#       if gas_tariff_code != None:
#         for meter in point["meters"]:
#           _LOGGER.info(f'Adding gas meter; mprn: {point["mprn"]}; serial number: {meter["serial_number"]}')
#           coordinator = create_reading_coordinator(hass, client, False, point["mprn"], meter["serial_number"])
#           entities.append(OctopusEnergyPreviousAccumulativeGasReading(coordinator, point["mprn"], meter["serial_number"], is_smets1))
#           entities.append(OctopusEnergyPreviousAccumulativeGasCost(coordinator, client, gas_tariff_code, point["mprn"], meter["serial_number"], is_smets1))
#           entities.append(OctopusEnergyGasCurrentRate(client, gas_tariff_code, point["mprn"], meter["serial_number"]))
#       else:
#         for meter in point["meters"]:
#           _LOGGER.info(f'Skipping gas meter due to no active agreement; mprn: {point["mprn"]}; serial number: {meter["serial_number"]}')
#         _LOGGER.info(f'agreements: {point["agreements"]}')
#   else:
#     _LOGGER.info('No gas meters available')

#   async_add_entities(entities, True)

# class OctopusEnergyElectricityCurrentRate(CoordinatorEntity, SensorEntity):
#   """Sensor for displaying the current rate."""

#   def __init__(self, coordinator, mpan, serial_number, is_export):
#     """Init sensor."""
#     # Pass coordinator to base class
#     super().__init__(coordinator)

#     self._mpan = mpan
#     self._serial_number = serial_number
#     self._is_export = is_export

#     self._attributes = {
#       "is_export": self._is_export
#     }

#     self._state = None

#   @property
#   def unique_id(self):
#     """The id of the sensor."""
#     return f"octopus_energy_electricity_{self._serial_number}_{self._mpan}_current_rate"
    
#   @property
#   def name(self):
#     """Name of the sensor."""
#     return f"Octopus Energy Electricity {self._serial_number} {self._mpan} Current Rate"

#   @property
#   def device_class(self):
#     """The type of sensor"""
#     return DEVICE_CLASS_MONETARY

#   @property
#   def icon(self):
#     """Icon of the sensor."""
#     return "mdi:currency-gbp"

#   @property
#   def unit_of_measurement(self):
#     """Unit of measurement of the sensor."""
#     return "GBP/kWh"

#   @property
#   def extra_state_attributes(self):
#     """Attributes of the sensor."""
#     return self._attributes

#   @property
#   def state(self):
#     """The state of the sensor."""
#     # Find the current rate. We only need to do this every half an hour
#     now = utcnow()
#     if (now.minute % 30) == 0 or self._state == None:
#       _LOGGER.info(f"Updating OctopusEnergyElectricityCurrentRate for '{self._mpan}/{self._serial_number}'")

#       current_rate = None
#       if self.coordinator.data != None:
#         rate = self.coordinator.data[self._mpan]
#         if rate != None:
#           for period in rate:
#             if now >= period["valid_from"] and now <= period["valid_to"]:
#               current_rate = period
#               break

#       if current_rate != None:
#         self._attributes = {
#           "rate": current_rate,
#           "is_export": self._is_export
#         }
        
#         self._state = current_rate["value_inc_vat"] / 100
#       else:
#         self._state = 0
#         self._attributes = {}

#     return self._state

# class OctopusEnergyElectricityPreviousRate(CoordinatorEntity, SensorEntity):
#   """Sensor for displaying the previous rate."""

#   def __init__(self, coordinator, mpan, serial_number, is_export):
#     """Init sensor."""
#     # Pass coordinator to base class
#     super().__init__(coordinator)

#     self._mpan = mpan
#     self._serial_number = serial_number
#     self._is_export = is_export

#     self._attributes = {
#       "is_export": self._is_export
#     }

#     self._state = None

#   @property
#   def unique_id(self):
#     """The id of the sensor."""
#     return f"octopus_energy_electricity_{self._serial_number}_{self._mpan}_previous_rate"
    
#   @property
#   def name(self):
#     """Name of the sensor."""
#     return f"Octopus Energy Electricity {self._serial_number} {self._mpan} Previous Rate"

#   @property
#   def device_class(self):
#     """The type of sensor"""
#     return DEVICE_CLASS_MONETARY

#   @property
#   def icon(self):
#     """Icon of the sensor."""
#     return "mdi:currency-gbp"

#   @property
#   def unit_of_measurement(self):
#     """Unit of measurement of the sensor."""
#     return "GBP/kWh"

#   @property
#   def extra_state_attributes(self):
#     """Attributes of the sensor."""
#     return self._attributes

#   @property
#   def state(self):
#     """The state of the sensor."""
#     # Find the previous rate. We only need to do this every half an hour
#     now = utcnow()
#     if (now.minute % 30) == 0 or self._state == None:
#       _LOGGER.info(f"Updating OctopusEnergyElectricityPreviousRate for '{self._mpan}/{self._serial_number}'")

#       target = now - timedelta(minutes=30)

#       previous_rate = None
#       if self.coordinator.data != None:
#         rate = self.coordinator.data[self._mpan]
#         if rate != None:
#           for period in rate:
#             if target >= period["valid_from"] and target <= period["valid_to"]:
#               previous_rate = period
#               break

#       if previous_rate != None:
#         self._attributes = {
#           "rate": previous_rate,
#           "is_export": self._is_export
#         }

#         self._state = previous_rate["value_inc_vat"] / 100
#       else:
#         self._state = 0
#         self._attributes = {}

#     return self._state

# class OctopusEnergyPreviousAccumulativeElectricityReading(CoordinatorEntity, SensorEntity):
#   """Sensor for displaying the previous days accumulative electricity reading."""

#   def __init__(self, coordinator, mpan, serial_number, is_export):
#     """Init sensor."""
#     super().__init__(coordinator)

#     self._mpan = mpan
#     self._serial_number = serial_number
#     self._is_export = is_export

#     self._attributes = {
#       "mpan": mpan,
#       "serial_number": serial_number,
#       "is_export": self._is_export
#     }

#     self._state = 0
#     self._latest_date = None

#   @property
#   def unique_id(self):
#     """The id of the sensor."""
#     return f"octopus_energy_electricity_{self._serial_number}_{self._mpan}_previous_accumulative_consumption"

#   @property
#   def name(self):
#     """Name of the sensor."""
#     return f"Octopus Energy Electricity {self._serial_number} {self._mpan} Previous Accumulative Consumption"

#   @property
#   def device_class(self):
#     """The type of sensor"""
#     return DEVICE_CLASS_ENERGY

#   @property
#   def state_class(self):
#     """The state class of sensor"""
#     return STATE_CLASS_TOTAL_INCREASING

#   @property
#   def unit_of_measurement(self):
#     """The unit of measurement of sensor"""
#     return ENERGY_KILO_WATT_HOUR

#   @property
#   def icon(self):
#     """Icon of the sensor."""
#     return "mdi:lightning-bolt"

#   @property
#   def extra_state_attributes(self):
#     """Attributes of the sensor."""
#     return self._attributes

#   @property
#   def state(self):
#     """Retrieve the previous days accumulative consumption"""
#     consumption = calculate_electricity_consumption(
#       self.coordinator.data,
#       self._latest_date
#     )

#     if (consumption != None):
#       _LOGGER.info(f"Calculated previous electricity consumption for '{self._mpan}/{self._serial_number}'...")
#       self._state = consumption["total"]
#       self._latest_date = consumption["last_calculated_timestamp"]

#       self._attributes = {
#         "mpan": self._mpan,
#         "serial_number": self._serial_number,
#         "is_export": self._is_export,
#         "total": consumption["total"],
#         "last_calculated_timestamp": consumption["last_calculated_timestamp"],
#         "charges": consumption["consumptions"]
#       }
    
#     return self._state

# class OctopusEnergyPreviousAccumulativeElectricityCost(CoordinatorEntity, SensorEntity):
#   """Sensor for displaying the previous days accumulative electricity cost."""

#   def __init__(self, coordinator, client, tariff_code, mpan, serial_number, is_export):
#     """Init sensor."""
#     super().__init__(coordinator)

#     self._mpan = mpan
#     self._serial_number = serial_number
#     self._is_export = is_export
#     self._client = client
#     self._tariff_code = tariff_code

#     self._attributes = {
#       "mpan": mpan,
#       "serial_number": serial_number,
#       "is_export": self._is_export
#     }

#     self._state = 0
#     self._latest_date = None

#   @property
#   def unique_id(self):
#     """The id of the sensor."""
#     return f"octopus_energy_electricity_{self._serial_number}_{self._mpan}_previous_accumulative_cost"
    
#   @property
#   def name(self):
#     """Name of the sensor."""
#     return f"Octopus Energy Electricity {self._serial_number} {self._mpan} Previous Accumulative Cost"

#   @property
#   def device_class(self):
#     """The type of sensor"""
#     return DEVICE_CLASS_MONETARY

#   @property
#   def state_class(self):
#     """The state class of sensor"""
#     return STATE_CLASS_TOTAL_INCREASING

#   @property
#   def unit_of_measurement(self):
#     """The unit of measurement of sensor"""
#     return "GBP"

#   @property
#   def icon(self):
#     """Icon of the sensor."""
#     return "mdi:currency-gbp"

#   @property
#   def extra_state_attributes(self):
#     """Attributes of the sensor."""
#     return self._attributes

#   @property
#   def should_poll(self):
#     return True

#   @property
#   def state(self):
#     """Retrieve the previously calculated state"""
#     return self._state

#   async def async_update(self):
#     current_datetime = now()
#     period_from = as_utc((current_datetime - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0))
#     period_to = as_utc(current_datetime.replace(hour=0, minute=0, second=0, microsecond=0))

#     consumption_cost = await async_calculate_electricity_cost(
#       self._client,
#       self.coordinator.data,
#       self._latest_date,
#       period_from,
#       period_to,
#       self._tariff_code
#     )

#     if (consumption_cost != None):
#       _LOGGER.info(f"Calculated previous electricity consumption cost for '{self._mpan}/{self._serial_number}'...")
#       self._latest_date = consumption_cost["last_calculated_timestamp"]
#       self._state = consumption_cost["total"]

#       self._attributes = {
#         "mpan": self._mpan,
#         "serial_number": self._serial_number,
#         "is_export": self._is_export,
#         "tariff_code": self._tariff_code,
#         "standing_charge": f'{consumption_cost["standing_charge"]}p',
#         "total_without_standing_charge": f'£{consumption_cost["total_without_standing_charge"]}',
#         "total": f'£{consumption_cost["total"]}',
#         "last_calculated_timestamp": consumption_cost["last_calculated_timestamp"],
#         "charges": consumption_cost["charges"]
#       }

# class OctopusEnergyGasCurrentRate(SensorEntity):
#   """Sensor for displaying the current rate."""

#   def __init__(self, client, tariff_code, mprn, serial_number):
#     """Init sensor."""

#     self._client = client
#     self._tariff_code = tariff_code
#     self._mprn = mprn
#     self._serial_number = serial_number

#     self._attributes = {
#       "mprn": self._mprn,
#       "serial_number": self._serial_number
#     }

#     self._state = None
#     self._latest_date = None

#   @property
#   def unique_id(self):
#     """The id of the sensor."""
#     return f'octopus_energy_gas_{self._serial_number}_{self._mprn}_current_rate';
    
#   @property
#   def name(self):
#     """Name of the sensor."""
#     return f'Octopus Energy Gas {self._serial_number} {self._mprn} Current Rate'

#   @property
#   def device_class(self):
#     """The type of sensor"""
#     return DEVICE_CLASS_MONETARY

#   @property
#   def icon(self):
#     """Icon of the sensor."""
#     return "mdi:currency-gbp"

#   @property
#   def unit_of_measurement(self):
#     """Unit of measurement of the sensor."""
#     return "GBP/kWh"

#   @property
#   def extra_state_attributes(self):
#     """Attributes of the sensor."""
#     return self._attributes

#   @property
#   def state(self):
#     """Retrieve the latest gas price"""
#     return self._state

#   async def async_update(self):
#     """Get the current price."""
#     # Find the current rate. We only need to do this every day

#     utc_now = utcnow()
#     if (self._latest_date == None or (self._latest_date + timedelta(days=1)) < utc_now):
#       _LOGGER.info('Updating OctopusEnergyGasCurrentRate')

#       period_from = as_utc(parse_datetime(utc_now.strftime("%Y-%m-%dT00:00:00Z")))
#       period_to = as_utc(parse_datetime((utc_now + timedelta(days=1)).strftime("%Y-%m-%dT00:00:00Z")))

#       rates = await self._client.async_get_gas_rates(self._tariff_code, period_from, period_to)
      
#       current_rate = None
#       if rates != None:
#         for period in rates:
#           if utc_now >= period["valid_from"] and utc_now <= period["valid_to"]:
#             current_rate = period
#             break

#       if current_rate != None:
#         self._state = current_rate["value_inc_vat"] / 100

#         # Adjust our period, as our gas only changes on a daily basis
#         current_rate["valid_from"] = period_from
#         current_rate["valid_to"] = period_to
#         self._attributes = current_rate
#       else:
#         self._state = 0
#         self._attributes = {}

#       self._latest_date = period_from

# class OctopusEnergyPreviousAccumulativeGasReading(CoordinatorEntity, SensorEntity):
#   """Sensor for displaying the previous days accumulative gas reading."""

#   def __init__(self, coordinator, mprn, serial_number, is_smets1_meter):
#     """Init sensor."""
#     super().__init__(coordinator)

#     self._mprn = mprn
#     self._serial_number = serial_number
#     self._is_smets1_meter = is_smets1_meter

#     self._attributes = {
#       "mprn": mprn,
#       "serial_number": serial_number,
#       "is_smets1_meter": is_smets1_meter
#     }

#     self._state = 0
#     self._latest_date = None

#   @property
#   def unique_id(self):
#     """The id of the sensor."""
#     return f"octopus_energy_gas_{self._serial_number}_{self._mprn}_previous_accumulative_consumption"
    
#   @property
#   def name(self):
#     """Name of the sensor."""
#     return f"Octopus Energy Gas {self._serial_number} {self._mprn} Previous Accumulative Consumption"

#   @property
#   def device_class(self):
#     """The type of sensor"""
#     return DEVICE_CLASS_GAS

#   @property
#   def state_class(self):
#     """The state class of sensor"""
#     return STATE_CLASS_TOTAL_INCREASING

#   @property
#   def unit_of_measurement(self):
#     """The unit of measurement of sensor"""
#     return VOLUME_CUBIC_METERS

#   @property
#   def icon(self):
#     """Icon of the sensor."""
#     return "mdi:fire"

#   @property
#   def extra_state_attributes(self):
#     """Attributes of the sensor."""
#     return self._attributes

#   @property
#   def state(self):
#     """Retrieve the previous days accumulative consumption"""
#     consumption = calculate_gas_consumption(
#       self.coordinator.data,
#       self._latest_date,
#       self._is_smets1_meter
#     )

#     if (consumption != None):
#       _LOGGER.info(f"Calculated previous gas consumption for '{self._mprn}/{self._serial_number}'...")
#       self._state = consumption["total_m3"]
#       self._latest_date = consumption["last_calculated_timestamp"]

#       self._attributes = {
#         "mprn": self._mprn,
#         "serial_number": self._serial_number,
#         "is_smets1_meter": self._is_smets1_meter,
#         "total_kwh": consumption["total_kwh"],
#         "total_m3": consumption["total_m3"],
#         "last_calculated_timestamp": consumption["last_calculated_timestamp"],
#         "charges": consumption["consumptions"]
#       }
    
#     return self._state

# class OctopusEnergyPreviousAccumulativeGasCost(CoordinatorEntity, SensorEntity):
#   """Sensor for displaying the previous days accumulative gas cost."""

#   def __init__(self, coordinator, client, tariff_code, mprn, serial_number, is_smets1_meter):
#     """Init sensor."""
#     super().__init__(coordinator)

#     self._mprn = mprn
#     self._serial_number = serial_number
#     self._client = client
#     self._tariff_code = tariff_code
#     self._is_smets1_meter = is_smets1_meter

#     self._attributes = {
#       "mpan": mprn,
#       "serial_number": serial_number,
#       "is_smets1_meter": is_smets1_meter
#     }

#     self._state = 0
#     self._latest_date = None

#   @property
#   def unique_id(self):
#     """The id of the sensor."""
#     return f"octopus_energy_gas_{self._serial_number}_{self._mprn}_previous_accumulative_cost"
    
#   @property
#   def name(self):
#     """Name of the sensor."""
#     return f"Octopus Energy Gas {self._serial_number} {self._mprn} Previous Accumulative Cost"

#   @property
#   def device_class(self):
#     """The type of sensor"""
#     return DEVICE_CLASS_MONETARY

#   @property
#   def state_class(self):
#     """The state class of sensor"""
#     return STATE_CLASS_TOTAL_INCREASING

#   @property
#   def unit_of_measurement(self):
#     """The unit of measurement of sensor"""
#     return "GBP"

#   @property
#   def icon(self):
#     """Icon of the sensor."""
#     return "mdi:currency-gbp"

#   @property
#   def extra_state_attributes(self):
#     """Attributes of the sensor."""
#     return self._attributes

#   @property
#   def should_poll(self):
#     return True

#   @property
#   def state(self):
#     """Retrieve the previously calculated state"""
#     return self._state

#   async def async_update(self):
#     current_datetime = now()
#     period_from = as_utc((current_datetime - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0))
#     period_to = as_utc(current_datetime.replace(hour=0, minute=0, second=0, microsecond=0))

#     consumption_cost = await async_calculate_gas_cost(
#       self._client,
#       self.coordinator.data,
#       self._latest_date,
#       period_from,
#       period_to,
#       {
#         "tariff_code": self._tariff_code,
#         "is_smets1_meter": self._is_smets1_meter
#       }
#     )

#     if (consumption_cost != None):
#       _LOGGER.info(f"Calculated previous gas consumption cost for '{self._mprn}/{self._serial_number}'...")
#       self._latest_date = consumption_cost["last_calculated_timestamp"]
#       self._state = consumption_cost["total"]

#       self._attributes = {
#         "mprn": self._mprn,
#         "serial_number": self._serial_number,
#         "tariff_code": self._tariff_code,
#         "is_smets1_meter": self._is_smets1_meter,
#         "standing_charge": f'{consumption_cost["standing_charge"]}p',
#         "total_without_standing_charge": f'£{consumption_cost["total_without_standing_charge"]}',
#         "total": f'£{consumption_cost["total"]}',
#         "last_calculated_timestamp": consumption_cost["last_calculated_timestamp"],
#         "charges": consumption_cost["charges"]
#       }
