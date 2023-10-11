from datetime import datetime, timedelta
import pytest

from unit import (create_rate_data, to_thirty_minute_increments)
from custom_components.carbon_intensity.target_rates import calculate_continuous_times

@pytest.mark.asyncio
@pytest.mark.parametrize("current_date,target_start_time,target_end_time,expected_first_valid_from,is_rolling_target",[
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T11:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T14:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), True),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-10T11:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), True),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T11:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T11:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), False),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-10T11:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), False),
  # No start set
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T02:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T14:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), True),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-10T02:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), True),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T02:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T02:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), False),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-10T02:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), False),
  # No end set
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T11:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T14:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), True),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T11:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T11:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), False),
  # No start or end set
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T02:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T14:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), True),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T02:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T02:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), False),
])
async def test_when_continuous_times_present_then_next_continuous_times_returned(current_date, target_start_time, target_end_time, expected_first_valid_from, is_rolling_target):
  # Arrange
  period_from = datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-02-11T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  expected_rates = [0.1, 0.2, 0.3, 0.2, 0.2, 0.1]

  rates = create_rate_data(
    period_from,
    period_to,
    expected_rates
  )
  
  # Restrict our time block
  target_hours = 1

  # Act
  result = calculate_continuous_times(
    current_date,
    target_start_time,
    target_end_time,
    target_hours,
    rates,
    is_rolling_target
  )

  # Assert
  assert result != None
  assert len(result) == 2
  assert result[0]["from"] == expected_first_valid_from
  assert result[0]["to"] == expected_first_valid_from + timedelta(minutes=30)
  assert result[0]["intensity_forecast"] == 0.1

  assert result[1]["from"] == expected_first_valid_from + timedelta(minutes=30)
  assert result[1]["to"] == expected_first_valid_from + timedelta(hours=1)
  assert result[1]["intensity_forecast"] == 0.1

@pytest.mark.asyncio
async def test_when_current_time_has_not_enough_time_left_then_no_continuous_times_returned():
  # Arrange
  period_from = datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-02-10T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  expected_rates = [0.1, 0.2, 0.3, 0.2, 0.2, 0.1]

  rates = create_rate_data(
    period_from,
    period_to,
    expected_rates
  )
  
  # Restrict our time block
  current_date = datetime.strptime("2022-02-09T17:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "10:00"
  target_end_time = "18:00"
  target_hours = 1

  # Act
  result = calculate_continuous_times(
    current_date,
    target_start_time,
    target_end_time,
    target_hours,
    rates
  )

  # Assert
  assert result != None
  assert len(result) == 0

@pytest.mark.asyncio
@pytest.mark.parametrize("current_date,target_start_time,target_end_time,expected_first_valid_from,is_rolling_target",[
  (datetime.strptime("2023-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2023-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False),
  (datetime.strptime("2023-01-01T01:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2023-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False),
  (datetime.strptime("2023-01-01T01:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2023-01-01T04:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), True),
  (datetime.strptime("2023-01-01T23:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, None, True),

  (datetime.strptime("2023-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "05:00", "19:00", datetime.strptime("2023-01-01T05:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False),
  (datetime.strptime("2023-01-01T06:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), "05:00", "19:00", datetime.strptime("2023-01-01T05:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False),
  (datetime.strptime("2023-01-01T06:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), "05:00", "19:00", datetime.strptime("2023-01-01T06:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), True),
  (datetime.strptime("2023-01-01T18:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "05:00", "19:00", datetime.strptime("2023-01-01T18:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True),
  (datetime.strptime("2023-01-01T18:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), "05:00", "19:00", None, True),

  (datetime.strptime("2023-01-01T20:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "20:00", "06:00", datetime.strptime("2023-01-01T23:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), False),
  (datetime.strptime("2023-01-02T02:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "20:00", "06:00", datetime.strptime("2023-01-01T23:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), False),
  (datetime.strptime("2023-01-02T02:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "20:00", "06:00", datetime.strptime("2023-01-02T04:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), True),
  (datetime.strptime("2023-01-02T05:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), "20:00", "06:00", None, True),
])
async def test_readme_examples(current_date, target_start_time, target_end_time, expected_first_valid_from, is_rolling_target):
  # Arrange
  rates = to_thirty_minute_increments(
    [
      {
        "intensity_forecast": 6,
        "from": "2023-01-01T00:00:00Z",
        "to": "2023-01-01T00:30:00Z"
      },
      {
        "intensity_forecast": 12,
        "from": "2023-01-01T00:30:00Z",
        "to": "2023-01-01T05:00:00Z"
      },
      {
        "intensity_forecast": 7,
        "from": "2023-01-01T05:00:00Z",
        "to": "2023-01-01T05:30:00Z"
      },
      {
        "intensity_forecast": 20,
        "from": "2023-01-01T05:30:00Z",
        "to": "2023-01-01T18:00:00Z"
      },
      {
        "intensity_forecast": 34,
        "from": "2023-01-01T18:00:00Z",
        "to": "2023-01-01T23:30:00Z"
      },
      {
        "intensity_forecast": 5,
        "from": "2023-01-01T23:30:00Z",
        "to": "2023-01-02T00:30:00Z"
      },
      {
        "intensity_forecast": 12,
        "from": "2023-01-02T00:30:00Z",
        "to": "2023-01-02T05:00:00Z"
      },
      {
        "intensity_forecast": 7,
        "from": "2023-01-02T05:00:00Z",
        "to": "2023-01-02T05:30:00Z"
      },
      {
        "intensity_forecast": 20,
        "from": "2023-01-02T05:30:00Z",
        "to": "2023-01-02T18:00:00Z"
      },
      {
        "intensity_forecast": 34,
        "from": "2023-01-02T18:00:00Z",
        "to": "2023-01-02T23:30:00Z"
      },
      {
        "intensity_forecast": 6,
        "from": "2023-01-02T23:30:00Z",
        "to": "2023-01-03T00:00:00Z"
      },
    ]
  )
  
  # Restrict our time block
  target_hours = 1

  # Act
  result = calculate_continuous_times(
    current_date,
    target_start_time,
    target_end_time,
    target_hours,
    rates,
    is_rolling_target
  )

  # Assert
  assert result != None

  if (expected_first_valid_from is None):
    assert len(result) == 0
  else:
    assert len(result) == 2
    assert result[0]["from"] == expected_first_valid_from
    assert result[0]["to"] == expected_first_valid_from + timedelta(minutes=30)
    assert result[1]["from"] == expected_first_valid_from + timedelta(minutes=30)
    assert result[1]["to"] == expected_first_valid_from + timedelta(minutes=60)

@pytest.mark.asyncio
async def test_when_last_rate_is_currently_active_and_target_is_rolling_then_rates_are_reevaluated():
  # Arrange
  current_date = datetime.strptime("2023-01-01T09:10:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "09:00"
  target_end_time = "22:00"

  expected_first_valid_from = datetime.strptime("2023-01-01T09:30:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  
  # Restrict our time block
  target_hours = 0.5

  rates = to_thirty_minute_increments(
    [
      {
        "intensity_forecast": 6,
        "from": "2023-01-01T00:00:00Z",
        "to": "2023-01-01T00:30:00Z"
      },
      {
        "intensity_forecast": 12,
        "from": "2023-01-01T00:30:00Z",
        "to": "2023-01-01T05:00:00Z"
      },
      {
        "intensity_forecast": 7,
        "from": "2023-01-01T05:00:00Z",
        "to": "2023-01-01T05:30:00Z"
      },
      {
        "intensity_forecast": 20,
        "from": "2023-01-01T05:30:00Z",
        "to": "2023-01-01T09:30:00Z"
      },
      {
        "intensity_forecast": 22,
        "from": "2023-01-01T09:30:00Z",
        "to": "2023-01-01T18:00:00Z"
      },
      {
        "intensity_forecast": 34,
        "from": "2023-01-01T18:00:00Z",
        "to": "2023-01-01T23:30:00Z"
      },
      {
        "intensity_forecast": 5,
        "from": "2023-01-01T23:30:00Z",
        "to": "2023-01-02T00:30:00Z"
      },
      {
        "intensity_forecast": 12,
        "from": "2023-01-02T00:30:00Z",
        "to": "2023-01-02T05:00:00Z"
      },
      {
        "intensity_forecast": 7,
        "from": "2023-01-02T05:00:00Z",
        "to": "2023-01-02T05:30:00Z"
      },
      {
        "intensity_forecast": 20,
        "from": "2023-01-02T05:30:00Z",
        "to": "2023-01-02T18:00:00Z"
      },
      {
        "intensity_forecast": 34,
        "from": "2023-01-02T18:00:00Z",
        "to": "2023-01-02T23:30:00Z"
      },
      {
        "intensity_forecast": 6,
        "from": "2023-01-02T23:30:00Z",
        "to": "2023-01-03T00:00:00Z"
      },
    ]
  )

  # Act
  result = calculate_continuous_times(
    current_date,
    target_start_time,
    target_end_time,
    target_hours,
    rates
  )

  # Assert
  assert result != None
  assert len(result) == 1
  assert result[0]["from"] == expected_first_valid_from
  assert result[0]["to"] == expected_first_valid_from + timedelta(minutes=30)
  assert result[0]["intensity_forecast"] == 22

@pytest.mark.asyncio
async def test_when_start_time_is_after_end_time_then_rates_are_overnight():
  # Arrange
  current_date = datetime.strptime("2023-01-01T09:10:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "20:00"
  target_end_time = "09:00"

  expected_first_valid_from = datetime.strptime("2023-01-01T23:30:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  
  # Restrict our time block
  target_hours = 1

  rates = to_thirty_minute_increments(
    [
      {
        "intensity_forecast": 6,
        "from": "2023-01-01T00:00:00Z",
        "to": "2023-01-01T00:30:00Z"
      },
      {
        "intensity_forecast": 12,
        "from": "2023-01-01T00:30:00Z",
        "to": "2023-01-01T05:00:00Z"
      },
      {
        "intensity_forecast": 7,
        "from": "2023-01-01T05:00:00Z",
        "to": "2023-01-01T05:30:00Z"
      },
      {
        "intensity_forecast": 20,
        "from": "2023-01-01T05:30:00Z",
        "to": "2023-01-01T18:00:00Z"
      },
      {
        "intensity_forecast": 34,
        "from": "2023-01-01T18:00:00Z",
        "to": "2023-01-01T23:30:00Z"
      },
      {
        "intensity_forecast": 5,
        "from": "2023-01-01T23:30:00Z",
        "to": "2023-01-02T00:30:00Z"
      },
      {
        "intensity_forecast": 12,
        "from": "2023-01-02T00:30:00Z",
        "to": "2023-01-02T05:00:00Z"
      },
      {
        "intensity_forecast": 7,
        "from": "2023-01-02T05:00:00Z",
        "to": "2023-01-02T05:30:00Z"
      },
      {
        "intensity_forecast": 20,
        "from": "2023-01-02T05:30:00Z",
        "to": "2023-01-02T18:00:00Z"
      },
      {
        "intensity_forecast": 34,
        "from": "2023-01-02T18:00:00Z",
        "to": "2023-01-02T23:30:00Z"
      },
      {
        "intensity_forecast": 6,
        "from": "2023-01-02T23:30:00Z",
        "to": "2023-01-03T00:00:00Z"
      },
    ]
  )

  # Act
  result = calculate_continuous_times(
    current_date,
    target_start_time,
    target_end_time,
    target_hours,
    rates,
    False
  )

  # Assert
  assert result != None
  assert len(result) == 2
  assert result[0]["from"] == expected_first_valid_from
  assert result[0]["to"] == expected_first_valid_from + timedelta(minutes=30)
  assert result[0]["intensity_forecast"] == 5

  assert result[1]["from"] == expected_first_valid_from + timedelta(minutes=30)
  assert result[1]["to"] == expected_first_valid_from + timedelta(minutes=60)
  assert result[1]["intensity_forecast"] == 5

@pytest.mark.asyncio
async def test_when_start_time_and_end_time_is_same_then_rates_are_shifted():
  # Arrange
  current_date = datetime.strptime("2023-01-01T17:10:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "16:00"
  target_end_time = "16:00"

  expected_first_valid_from = datetime.strptime("2023-01-01T23:30:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  
  # Restrict our time block
  target_hours = 1

  rates = to_thirty_minute_increments(
    [
      {
        "intensity_forecast": 6,
        "from": "2023-01-01T00:00:00Z",
        "to": "2023-01-01T00:30:00Z"
      },
      {
        "intensity_forecast": 12,
        "from": "2023-01-01T00:30:00Z",
        "to": "2023-01-01T05:00:00Z"
      },
      {
        "intensity_forecast": 7,
        "from": "2023-01-01T05:00:00Z",
        "to": "2023-01-01T05:30:00Z"
      },
      {
        "intensity_forecast": 20,
        "from": "2023-01-01T05:30:00Z",
        "to": "2023-01-01T18:00:00Z"
      },
      {
        "intensity_forecast": 34,
        "from": "2023-01-01T18:00:00Z",
        "to": "2023-01-01T23:30:00Z"
      },
      {
        "intensity_forecast": 5,
        "from": "2023-01-01T23:30:00Z",
        "to": "2023-01-02T00:30:00Z"
      },
      {
        "intensity_forecast": 12,
        "from": "2023-01-02T00:30:00Z",
        "to": "2023-01-02T05:00:00Z"
      },
      {
        "intensity_forecast": 7,
        "from": "2023-01-02T05:00:00Z",
        "to": "2023-01-02T05:30:00Z"
      },
      {
        "intensity_forecast": 20,
        "from": "2023-01-02T05:30:00Z",
        "to": "2023-01-02T18:00:00Z"
      },
      {
        "intensity_forecast": 34,
        "from": "2023-01-02T18:00:00Z",
        "to": "2023-01-02T23:30:00Z"
      },
      {
        "intensity_forecast": 6,
        "from": "2023-01-02T23:30:00Z",
        "to": "2023-01-03T00:00:00Z"
      },
    ]
  )

  # Act
  result = calculate_continuous_times(
    current_date,
    target_start_time,
    target_end_time,
    target_hours,
    rates,
    False
  )

  # Assert
  assert result != None
  assert len(result) == 2
  assert result[0]["from"] == expected_first_valid_from
  assert result[0]["to"] == expected_first_valid_from + timedelta(minutes=30)
  assert result[0]["intensity_forecast"] == 5

  assert result[1]["from"] == expected_first_valid_from + timedelta(minutes=30)
  assert result[1]["to"] == expected_first_valid_from + timedelta(minutes=60)
  assert result[1]["intensity_forecast"] == 5


@pytest.mark.asyncio
async def test_when_start_time_is_after_end_time_and_rolling_target_then_rates_are_overnight():
  # Arrange
  current_date = datetime.strptime("2022-10-21T23:30:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "22:00"
  target_end_time = "01:00"

  expected_first_valid_from = datetime.strptime("2022-10-21T23:30:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  
  # Restrict our time block
  target_hours = 1

  rates = to_thirty_minute_increments(
    [
      {
        "intensity_forecast": 15.1,
        "from": "2022-10-21T00:00:00Z",
        "to": "2022-10-21T22:00:00Z"
      },
      {
        "intensity_forecast": 16.1,
        "from": "2022-10-21T22:00:00Z",
        "to": "2022-10-22T02:00:00Z"
      },
      {
        "intensity_forecast": 15.1,
        "from": "2022-10-22T02:00:00Z",
        "to": "2022-10-22T05:00:00Z"
      },
    ]
  )

  # Act
  result = calculate_continuous_times(
    current_date,
    target_start_time,
    target_end_time,
    target_hours,
    rates,
    True
  )

  # Assert
  assert result != None
  assert len(result) == 2
  assert result[0]["from"] == expected_first_valid_from
  assert result[0]["to"] == expected_first_valid_from + timedelta(minutes=30)
  assert result[0]["intensity_forecast"] == 16.1

  assert result[1]["from"] == expected_first_valid_from + timedelta(minutes=30)
  assert result[1]["to"] == expected_first_valid_from + timedelta(minutes=60)
  assert result[1]["intensity_forecast"] == 16.1

@pytest.mark.asyncio
async def test_when_start_time_and_end_time_is_same_and_rolling_target_then_rates_are_shifted():
  # Arrange
  current_date = datetime.strptime("2022-10-21T23:30:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "16:00"
  target_end_time = "16:00"

  expected_first_valid_from = datetime.strptime("2022-10-22T02:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  
  # Restrict our time block
  target_hours = 1

  rates = to_thirty_minute_increments(
    [
      {
        "intensity_forecast": 15.1,
        "from": "2022-10-21T00:00:00Z",
        "to": "2022-10-21T22:00:00Z"
      },
      {
        "intensity_forecast": 16.1,
        "from": "2022-10-21T22:00:00Z",
        "to": "2022-10-22T02:00:00Z"
      },
      {
        "intensity_forecast": 15.1,
        "from": "2022-10-22T02:00:00Z",
        "to": "2022-10-22T05:00:00Z"
      },
      {
        "intensity_forecast": 16.1,
        "from": "2022-10-22T05:00:00Z",
        "to": "2022-10-23T00:00:00Z"
      },
    ]
  )

  # Act
  result = calculate_continuous_times(
    current_date,
    target_start_time,
    target_end_time,
    target_hours,
    rates,
    True
  )

  # Assert
  assert result != None
  assert len(result) == 2
  assert result[0]["from"] == expected_first_valid_from
  assert result[0]["to"] == expected_first_valid_from + timedelta(minutes=30)
  assert result[0]["intensity_forecast"] == 15.1

@pytest.mark.asyncio
async def test_when_available_rates_are_too_low_then_no_times_are_returned():
  # Arrange
  current_date = datetime.strptime("2022-10-22T22:40:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "16:00"
  target_end_time = "16:00"
  
  # Restrict our time block
  target_hours = 3

  rates = to_thirty_minute_increments(
    [
      {
        "intensity_forecast": 15.1,
        "from": "2022-10-21T00:00:00Z",
        "to": "2022-10-21T22:00:00Z"
      },
      {
        "intensity_forecast": 16.1,
        "from": "2022-10-21T22:00:00Z",
        "to": "2022-10-22T02:00:00Z"
      },
      {
        "intensity_forecast": 15.1,
        "from": "2022-10-22T02:00:00Z",
        "to": "2022-10-22T05:00:00Z"
      },
      {
        "intensity_forecast": 16.1,
        "from": "2022-10-22T05:00:00Z",
        "to": "2022-10-23T00:00:00Z"
      },
    ]
  )

  # Act
  result = calculate_continuous_times(
    current_date,
    target_start_time,
    target_end_time,
    target_hours,
    rates,
    False
  )

  # Assert
  assert result != None
  assert len(result) == 0