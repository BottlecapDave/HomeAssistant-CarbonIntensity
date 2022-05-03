from datetime import datetime, timedelta
import mock
import pytest
from tests.unit import create_rate_data

from unit import (create_consumption_data)
from custom_components.octopus_energy.sensor_utils import async_calculate_gas_cost
from custom_components.octopus_energy.api_client import OctopusEnergyApiClient

@pytest.mark.asyncio
async def test_when_gas_consumption_is_none_then_no_calculation_is_returned():
  # Arrange
  client = OctopusEnergyApiClient("NOT_REAL")
  period_from = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-03-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  latest_date = datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  is_smets1_meter = True
  tariff_code = "G-1R-SUPER-GREEN-24M-21-07-30-A"

  # Act
  consumption_cost = await async_calculate_gas_cost(
    client,
    None,
    latest_date,
    period_from,
    period_to,
    {
      "tariff_code": tariff_code,
      "is_smets1_meter": is_smets1_meter
    }
  )

  # Assert
  assert consumption_cost == None

@pytest.mark.asyncio
async def test_when_gas_consumption_is_empty_then_no_calculation_is_returned():
  # Arrange
  client = OctopusEnergyApiClient("NOT_REAL")
  period_from = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-03-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  latest_date = datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  is_smets1_meter = True
  tariff_code = "G-1R-SUPER-GREEN-24M-21-07-30-A"

  # Act
  consumption_cost = await async_calculate_gas_cost(
    client,
    [],
    latest_date,
    period_from,
    period_to,
    {
      "tariff_code": tariff_code,
      "is_smets1_meter": is_smets1_meter
    }
  )

  # Assert
  assert consumption_cost == None

@pytest.mark.asyncio
async def test_when_gas_consumption_is_before_latest_date_then_no_calculation_is_returned():
  # Arrange
  client = OctopusEnergyApiClient("NOT_REAL")
  period_from = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-03-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  latest_date = datetime.strptime("2022-03-02T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  is_smets1_meter = True
  tariff_code = "G-1R-SUPER-GREEN-24M-21-07-30-A"

  consumption_data = create_consumption_data(period_from, period_to)
  assert consumption_data != None
  assert len(consumption_data) > 0

  # Act
  consumption_cost = await async_calculate_gas_cost(
    client,
    consumption_data,
    latest_date,
    period_from,
    period_to,
    {
      "tariff_code": tariff_code,
      "is_smets1_meter": is_smets1_meter
    }
  )

  # Assert
  assert consumption_cost == None

@pytest.mark.asyncio
@pytest.mark.parametrize("is_smets1_meter,latest_date",[
  (True, datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")), 
  (True, None), 
  (False, datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")), 
  (False, None)
])
async def test_when_gas_consumption_available_then_calculation_returned(is_smets1_meter, latest_date):
  # Arrange
  
  period_from = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-03-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")

  # Price is in pence
  expected_rate_price = 50

  async def async_mocked_get_gas_rates(*args, **kwargs):
    return create_rate_data(period_from, period_to, [expected_rate_price])

  expected_standing_charge = {
    "value_exc_vat": 1,
    "value_inc_vat": 2
  }

  async def async_mocked_get_gas_standing_charge(*args, **kwargs):
    return expected_standing_charge

  with mock.patch.multiple(OctopusEnergyApiClient, async_get_gas_rates=async_mocked_get_gas_rates, async_get_gas_standing_charge=async_mocked_get_gas_standing_charge):
    client = OctopusEnergyApiClient("NOT_REAL")

    tariff_code = "G-1R-SUPER-GREEN-24M-21-07-30-A"
    
    consumption_data = create_consumption_data(period_from, period_to)
    assert consumption_data != None
    assert len(consumption_data) > 0
    assert consumption_data[-1]["interval_end"] == period_to
    assert consumption_data[0]["interval_start"] == period_from

    # Make sure we have rates and standing charges available
    rates = await client.async_get_gas_rates(tariff_code, period_from, period_to)
    assert rates != None
    assert len(rates) > 0

    standard_charge_result = await client.async_get_gas_standing_charge(tariff_code, period_from, period_to)
    assert standard_charge_result != None

    # Act
    consumption_cost = await async_calculate_gas_cost(
      client,
      consumption_data,
      latest_date,
      period_from,
      period_to,
      {
        "tariff_code": tariff_code,
        "is_smets1_meter": is_smets1_meter
      }
    )

    # Assert
    assert consumption_cost != None
    assert len(consumption_cost["charges"]) == 48

    assert consumption_cost["standing_charge"] == expected_standing_charge["value_inc_vat"]
    
    assert consumption_cost["last_calculated_timestamp"] == consumption_data[-1]["interval_end"]
    
    # Check that for SMETS2 meters, we convert the data from m3 to kwh
    if is_smets1_meter:
      
      # Total is reported in pounds and pence, but rate prices are in pence, so we need to calculate our expected value
      assert consumption_cost["total_without_standing_charge"] == round((48 * expected_rate_price) / 100, 2)
      assert consumption_cost["total"] == round(((48 * expected_rate_price) + expected_standing_charge["value_inc_vat"]) / 100, 2)
    else:
      # Total is reported in pounds and pence, but rate prices are in pence, so we need to calculate our expected value
      expected_total_values = 11.363
      assert consumption_cost["total_without_standing_charge"] == round((expected_total_values * 48 * expected_rate_price) / 100, 2)
      assert consumption_cost["total"] == round(((expected_total_values * 48 * expected_rate_price) + expected_standing_charge["value_inc_vat"]) / 100, 2)

    # Make sure our data is returned in 30 minute increments
    expected_valid_from = period_from
    for item in consumption_cost["charges"]:
      expected_valid_to = expected_valid_from + timedelta(minutes=30)

      assert "from" in item
      assert item["from"] == expected_valid_from
      assert "to" in item
      assert item["to"] == expected_valid_to

      expected_valid_from = expected_valid_to

@pytest.mark.asyncio
async def test_when_gas_consumption_starting_at_latest_date_then_calculation_returned():
  # Arrange
  period_from = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-03-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")

  # Price is in pence
  expected_rate_price = 50

  async def async_mocked_get_gas_rates(*args, **kwargs):
    return create_rate_data(period_from, period_to, [expected_rate_price])

  expected_standing_charge = {
    "value_exc_vat": 1,
    "value_inc_vat": 2
  }

  async def async_mocked_get_gas_standing_charge(*args, **kwargs):
    return expected_standing_charge

  with mock.patch.multiple(OctopusEnergyApiClient, async_get_gas_rates=async_mocked_get_gas_rates, async_get_gas_standing_charge=async_mocked_get_gas_standing_charge):
    client = OctopusEnergyApiClient("NOT_REAL")
    tariff_code = "G-1R-SUPER-GREEN-24M-21-07-30-A"
    latest_date = None
    is_smets1_meter = True
    
    consumption_data = create_consumption_data(period_from, period_to, True)
    assert consumption_data != None
    assert len(consumption_data) > 0
    assert consumption_data[0]["interval_end"] == period_to
    assert consumption_data[-1]["interval_start"] == period_from

    # Make sure we have rates and standing charges available
    rates = await client.async_get_gas_rates(tariff_code, period_from, period_to)
    assert rates != None
    assert len(rates) > 0

    standard_charge_result = await client.async_get_gas_standing_charge(tariff_code, period_from, period_to)
    assert standard_charge_result != None

    # Act
    consumption_cost = await async_calculate_gas_cost(
      client,
      consumption_data,
      latest_date,
      period_from,
      period_to,
      {
        "tariff_code": tariff_code,
        "is_smets1_meter": is_smets1_meter
      }
    )

    # Assert
    assert consumption_cost != None
    assert len(consumption_cost["charges"]) == 48

    assert consumption_cost["last_calculated_timestamp"] == consumption_data[0]["interval_end"]
    assert consumption_cost["standing_charge"] == expected_standing_charge["value_inc_vat"]

    # Total is reported in pounds and pence, but rate prices are in pence, so we need to calculate our expected value
    assert consumption_cost["total_without_standing_charge"] == round((48 * expected_rate_price) / 100, 2)
    assert consumption_cost["total"] == round(((48 * expected_rate_price) + expected_standing_charge["value_inc_vat"]) / 100, 2)

    # Make sure our data is returned in 30 minute increments
    expected_valid_from = period_from
    for item in consumption_cost["charges"]:
      expected_valid_to = expected_valid_from + timedelta(minutes=30)

      assert "from" in item
      assert item["from"] == expected_valid_from
      assert "to" in item
      assert item["to"] == expected_valid_to

      expected_valid_from = expected_valid_to