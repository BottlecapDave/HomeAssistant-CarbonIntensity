from datetime import datetime, timedelta
import os
import pytest

from custom_components.carbon_intensity.api_client import CarbonIntensityApiClient

@pytest.mark.asyncio
@pytest.mark.parametrize("region",[
  (1),
  (2),
  (3),
  (4),
  (5),
  (6),
  (7),
  (8),
  (9),
  (10),
  (11),
  (12),
  (13),
  (14),
  (15),
  (16),
  (17)
])
async def test_when_get_intensity_and_generation_rate_called_then_calculation_returned(region):
    # Arrange
    client = CarbonIntensityApiClient()
    period_from = datetime.strptime("2021-12-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")

    # Act
    data = await client.async_get_intensity_and_generation_rates(period_from, region)

    # Assert
    assert len(data) == 97

    # Make sure our data is returned in 30 minute increments
    expected_from = period_from - timedelta(minutes=30)
    for item in data:
        expected_to = expected_from + timedelta(minutes=30)

        assert "from" in item
        assert item["from"] == expected_from
        assert "to" in item
        assert item["to"] == expected_to
        assert "intensity_forecast" in item
        assert "generation_mix" in item

        expected_from = expected_to