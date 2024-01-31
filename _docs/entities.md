# Entities

## Current Rating

`sensor.carbon_intensity_{{REGION}}_current_rating`

The forecasted intensity rating of the current 30 minute period.

| Attribute | Type | Description |
|-----------|------|-------------|
| `rate` | `object` | The rate for the current 30 minute period |

For the rate, you will get the following attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `from` | `string` | The time the rate starts. |
| `to` | `string` | The time the rate ends. |
| `intensity_forecast` | `integer` | The forecasted/estimated carbon intensity for the period of time. The higher the number, the more carbon. |
| `generation_mix` | `list` | The splits between the different fuel sources. |

For each generation mix, you will get the following attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `fuel` | `string` | The type of fuel |
| `perc` | `float` | The estimated percentage the fuel source makes up in the mix. |

## Current Day Rates

`event.carbon_intensity_{{REGION}}_current_day_rates`

The state of this sensor states when the current day's rates were last updated. The attributes of this sensor exposes the current day's rates.

| Attribute | Type | Description |
|-----------|------|-------------|
| `rates` | `list` | The collection of rates for the current day |

For each rate, you will get the following attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `from` | `string` | The time the rate starts. |
| `to` | `string` | The time the rate ends. |
| `intensity_forecast` | `integer` | The forecasted/estimated carbon intensity for the period of time. The higher the number, the more carbon. |
| `generation_mix` | `list` | The splits between the different fuel sources. |

For each generation mix, you will get the following attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `fuel` | `string` | The type of fuel |
| `perc` | `float` | The estimated percentage the fuel source makes up in the mix. |

## Next Day Rates

`event.carbon_intensity_{{REGION}}_next_day_rates`

The state of this sensor states when the next day's rates were last updated. The attributes of this sensor exposes the next day's rates.

| Attribute | Type | Description |
|-----------|------|-------------|
| `rates` | `list` | The collection of rates for the next day |

For each rate, you will get the following attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `from` | `string` | The time the rate starts. |
| `to` | `string` | The time the rate ends. |
| `intensity_forecast` | `integer` | The forecasted/estimated carbon intensity for the period of time. The higher the number, the more carbon. |
| `generation_mix` | `list` | The splits between the different fuel sources. |

For each generation mix, you will get the following attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `fuel` | `string` | The type of fuel |
| `perc` | `float` | The estimated percentage the fuel source makes up in the mix. |