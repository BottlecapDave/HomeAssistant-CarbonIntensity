import os
from datetime import timedelta

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
