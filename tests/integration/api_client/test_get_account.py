from datetime import datetime, timedelta
import os
import pytest

from integration import get_test_context
from custom_components.octopus_energy.api_client import OctopusEnergyApiClient

@pytest.mark.asyncio
async def test_when_get_account_is_called_then_electricity_and_gas_points_returned():
    # Arrange
    context = get_test_context()

    client = OctopusEnergyApiClient(context["api_key"])
    account_id = context["account_id"]

    # Act
    account = await client.async_get_account(account_id)

    # Assert
    assert "electricity_meter_points" in account
    
    assert len(account["electricity_meter_points"]) == 1
    meter_point = account["electricity_meter_points"][0]
    assert meter_point["mpan"] == context["electricity_mpan"]
    assert meter_point["is_export"] == False
    
    assert len(meter_point["meters"]) == 1
    meter = meter_point["meters"][0]
    assert meter["serial_number"] == context["electricity_serial_number"]
    
    assert "gas_meter_points" in account
    assert len(account["gas_meter_points"]) == 1
    meter_point = account["gas_meter_points"][0]
    assert meter_point["mprn"] == context["gas_mprn"]
    
    assert len(meter_point["meters"]) == 1
    meter = meter_point["meters"][0]
    assert meter["serial_number"] == context["gas_serial_number"]