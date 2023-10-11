# Services

- [Services](#services)
  - [Service carbon\_intensity.update\_target\_config](#service-carbon_intensityupdate_target_config)

There are a few services available within this integration, which are detailed here.

## Service carbon_intensity.update_target_config

Service for updating a given target rate's config. This allows you to change target rates sensors dynamically based on other outside criteria (e.g. you need to adjust the target hours to top up home batteries).

> Please note this is temporary and will not persist between restarts.

| Attribute          | Optional | Description                                                                                                    |
| ------------------ | -------- | ---------------------------------------------------------------------------------------------------------------|
| `target.entity_id` | `no`     | The name of the target sensor whose configuration is to be updated                                             |
| `data.hours`       | `yes`    | The optional number of hours the rate sensor should come on during a 24 hour period. Must be divisible by 0.5. |
| `data.start_time`  | `yes`    | The optional time the evaluation period should start. Must be in the format of `HH:MM`.                        |
| `data.end_time`    | `yes`    | The optional time the evaluation period should end. Must be in the format of `HH:MM`.                          |
| `data.offset`      | `yes`    | The optional offset to apply to the target rate when it starts. Must be in the format `(+/-)HH:MM:SS`          |

This can be used via automations in the following way. Assuming we have the following inputs.

```yaml
input_number:
  carbon_intensity_hours:
    name: Carbon Intensity Target Hours
    min: 0
    max: 24

input_text:
  # From/to would ideally use input_datetime, but we need the time in a different format
  carbon_intensity_from:
    name: Carbon Intensity Target From
    initial: "00:00"
  carbon_intensity_to:
    name: Carbon Intensity Target To
    initial: "00:00"
  carbon_intensity_offset:
    name: Carbon Intensity Target Offset
    initial: "-00:00:00"
```

Then an automation might look like the following

```yaml
automations:
  - alias: Update target rate config
    trigger:
    - platform: state
      entity_id:
      - input_number.carbon_intensity_hours
      - input_text.carbon_intensity_from
      - input_text.carbon_intensity_to
      - input_text.carbon_intensity_offset
    condition: []
    action:
    - service: carbon_intensity.update_target_config
      data:
        hours: >
          "{{ states('input_number.carbon_intensity_hours') | string }}"
        start_time: >
          {{ states('input_text.carbon_intensity_from') }}
        end_time: >
          {{ states('input_text.carbon_intensity_to') }}
        offset: >
          {{ states('input_text.carbon_intensity_offset') }}
      target:
        entity_id: binary_sensor.carbon_intensity_target_example
```
