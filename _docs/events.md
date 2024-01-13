# Events

The following events are raised by the integration. These events power various entities mentioned above. They can also be used to trigger automations. An example automation might look like the following

```yaml
- alias: CI rates change
  trigger:
  - platform: event
    event_type: carbon_intensity_next_day_rates
  condition: []
  action:
  - event: notify_channels
    event_data_template:
      mode: message
      title: OE price changes
      message: >
        New rates available for {{ trigger.event.data.region }}. Starting value is {{ trigger.event.data.rates[0]["intensity_forecast"] }}
      target: <@ULU7111GU>
      length_hint: 00:00:04
```

## Current Day Rates

`carbon_intensity_current_day_rates`

This is fired when the current day rates are updated.

| Attribute | Type | Description |
|-----------|------|-------------|
| `rates` | `list` | The list of rates applicable for the current day |
| `region` | `string` | The region the rates are for |

## Next Day Rates

`carbon_intensity_next_day_rates`

This is fired when the next day rates are updated.

| Attribute | Type | Description |
|-----------|------|-------------|
| `rates` | `list` | The list of rates applicable for the next day |
| `region` | `string` | The region the rates are for |