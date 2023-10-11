import logging
import json
import aiohttp
from homeassistant.util.dt import (as_utc, parse_datetime)

_LOGGER = logging.getLogger(__name__)

class CarbonIntensityApiClient:

  def __init__(self):
    self._base_url = 'https://api.carbonintensity.org.uk'

  async def async_get_intensity_and_generation_rates(self, period_from, region):
    """Get the intensity and generation rates"""
    results = []
    async with aiohttp.ClientSession() as client:
      url = f'{self._base_url}/regional/intensity/{period_from.strftime("%Y-%m-%dT%H:%M:%SZ")}/fw48h/regionid/{region}'
      async with client.get(url) as response:
        try:
          data = await self.__async_read_response(response, url, { "data": [] })
          if ("data" in data and "data" in data["data"]):
            for item in data["data"]["data"]:
              results.append({
                "from": as_utc(parse_datetime(item["from"])),
                "to": as_utc(parse_datetime(item["to"])),
                "intensity_forecast": int(item["intensity"]["forecast"]),
                "generation_mix": item["generationmix"]
              })
        except:
          _LOGGER.error(f'Failed to extract intensity and generation rates: {url}')
          raise

    return results

  async def __async_read_response(self, response, url, default_value):
    """Reads the response, logging any json errors"""
    if response.status >= 500:
      _LOGGER.debug(f'Server error: {url}')
      return default_value

    text = await response.text()
    try:
      return json.loads(text)
    except:
      raise Exception(f'Failed to extract response json: {url}; {text}')
