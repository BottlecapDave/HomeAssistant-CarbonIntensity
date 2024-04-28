from datetime import timedelta

import re

from ..const import (
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
    
def get_region_options():
  return {
    "0": "National",
    "1": "North Scotland",
    "2": "South Scotland",
    "3": "North West England",
    "4": "North East England",
    "5": "Yorkshire",
    "6": "North Wales",
    "7": "South Wales",
    "8": "West Midlands",
    "9": "East Midlands",
    "10": "East England",
    "11": "South West England",
    "12": "South England",
    "13": "London",
    "14": "South East England",
    "15": "England",
    "16": "Scotland",
    "17": "Wales"
  }

def get_region_from_id(region_number):
  regions = get_region_options()
  return regions[region_number]

def get_region_for_unique_id_from_id(region_number):
  return get_region_from_id(region_number).replace(' ', '')