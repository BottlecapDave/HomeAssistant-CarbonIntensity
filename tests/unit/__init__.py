import os
from datetime import datetime, timedelta

def create_rate_data(period_from, period_to, expected_rates: list):
  rates = []
  current_valid_from = period_from
  current_valid_to = None

  rate_index = 0
  while current_valid_to == None or current_valid_to < period_to:
    current_valid_to = current_valid_from + timedelta(minutes=30)

    rates.append({
      "from": current_valid_from,
      "to": current_valid_to,
      "intensity_forecast": expected_rates[rate_index]
    })

    current_valid_from = current_valid_to
    rate_index = rate_index + 1

    if (rate_index > (len(expected_rates) - 1)):
      rate_index = 0

  return rates

def get_from(rate):
  return rate["from"]

def to_thirty_minute_increments(initial_rates: list):
  rates = []

  for rate in initial_rates:
    current_from = datetime.strptime(rate["from"], "%Y-%m-%dT%H:%M:%S%z")
    target_to = datetime.strptime(rate["to"], "%Y-%m-%dT%H:%M:%S%z")
    while current_from < target_to:
      current_to = current_from + timedelta(minutes=30)
      rates.append({
        "intensity_forecast": rate["intensity_forecast"],
        "from": current_from,
        "to": current_to
      })
      current_from = current_to
  
  rates.sort(key=get_from)
  return rates