from datetime import timedelta

import re

from .const import (
  REGEX_OFFSET_PARTS,
)

def apply_offset(date_time, offset, inverse = False):
  matches = re.search(REGEX_OFFSET_PARTS, offset)
  if matches == None:
    raise Exception(f'Unable to extract offset: {offset}')

  symbol = matches[1]
  hours = float(matches[2])
  minutes = float(matches[3])
  seconds = float(matches[4])

  if ((symbol == "-" and inverse == False) or (symbol != "-" and inverse == True)):
    return date_time - timedelta(hours=hours, minutes=minutes, seconds=seconds)
  
  return date_time + timedelta(hours=hours, minutes=minutes, seconds=seconds)
    