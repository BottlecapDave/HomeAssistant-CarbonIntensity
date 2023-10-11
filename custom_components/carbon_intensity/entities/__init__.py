from datetime import datetime

def get_current_rate(current: datetime, rates: list):
  current_rate = None
  if rates is not None:
    for period in rates:
      if current >= period["from"] and current <= period["to"]:
        current_rate = period
        break

  return current_rate

  if current_rate != None:
    self._attributes = {
      "rate": current_rate,
    }
    
    if current_rate != None:
      self._state = current_rate["intensity_forecast"]