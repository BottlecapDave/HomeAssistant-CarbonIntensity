# Home Assistant Carbon Intensity

[![installation_badge](https://img.shields.io/badge/dynamic/json?color=41BDF5&logo=home-assistant&label=integration%20usage&suffix=%20installs&cacheSeconds=15600&url=https://analytics.home-assistant.io/custom_integrations.json&query=$.carbon_intensity.total)](https://github.com/hacs/integration)

Custom component to use the data from [carbonintensity.org.uk](https://carbonintensity.org.uk) to make your home more energy efficient.

- [Home Assistant Carbon Intensity](#home-assistant-carbon-intensity)
  - [How to install](#how-to-install)
    - [HACS](#hacs)
    - [Manual](#manual)
  - [How to setup](#how-to-setup)
    - [Your Settings](#your-settings)
    - [Target Rates](#target-rates)
      - [From and To times](#from-and-to-times)
      - [Offset](#offset)
      - [Rolling Target](#rolling-target)
      - [Examples](#examples)
        - [Continuous](#continuous)
        - [Intermittent](#intermittent)
  - [Services](#services)
    - [Service carbon\_intensity.update\_target\_config](#service-carbon_intensityupdate_target_config)
  - [FAQ](#faq)
    - [I'm having issues with the integration](#im-having-issues-with-the-integration)

## How to install

You should take the latest published [release](https://github.com/BottlecapDave/HomeAssistant-CarbonIntensity/releases). The current state of `develop` will be in flux and therefore possibly subject to change.

### HACS

While the integration isn't available in the HACS store yet, you can install it as a [custom repository](https://hacs.xyz/docs/faq/custom_repositories), providing the url `https://github.com/BottlecapDave/HomeAssistant-CarbonIntensity` and category of `integration`. Once installed, don't forget to restart your home assistant instance for the integration to be picked up.

### Manual

To install, place the contents of `custom_components` into the `<config directory>/custom_components` folder of your Home Assistant installation.

## How to setup

Setup is done entirely via the [integration UI](https://my.home-assistant.io/redirect/config_flow_start/?domain=carbon_intensity).

### Your Settings

The first thing you'll be asked to setup when you add the integration is to setup your region. This will be used to work out the carbon intensity in your area.

After completing, you'll get the following sensors:

* `sensor.carbon_intensity_current_rating` - The forecasted intensity rating of the current 30 minute period. All other forecasted intensity ratings are also available as an attribute of this sensor.

### Target Rates

If you go through the [setup](https://my.home-assistant.io/redirect/config_flow_start/?domain=carbon_intensity) process after you've configured your setup, you can set up target rate sensors. These sensors calculate the lowest continuous or intermittent rates **within a 24 hour period** and turn on when these periods are active. These sensors can then be used in automations to turn on/off devices to reduce intensity on the grid and reduce carbon output.

Each sensor will be in the form `binary_sensor.carbon_intensity_target_{{TARGET_RATE_NAME}}`.

#### From and To times

If you're wanting your devices to come on during a certain period, for example while you're at work, you can set the minimum and/or maximum times for your target rate sensor. These are specified in 24 hour clock format and will attempt to find the optimum discovered period during these times.

If not specified, these default from `00:00:00` to `23:59:59`. However you can use this feature to change this evaluation period. 

If for example you want to look at rates overnight you could set your from time to something like `20:00` and your `to` time to something like `05:00`. If you're wanting to "shift" the evaluation period, you could set your `from` and `to` to something like `16:00`.

See the examples below for how this might work.

#### Offset

You may want your target rate sensors to turn on a period of time before the optimum discovered period. For example, you may be turning on a robot vacuum cleaner for a 30 minute clean and want it to charge during the optimum period. For this, you'd use the `offset` field and set it to `-00:30:00`, which can be both positive and negative and go up to a maximum of 24 hours. This will shift when the sensor turns on relative to the optimum period. For example, if the optimum period is between `2023-01-18T10:00` and `2023-01-18T11:00` with an offset of `-00:30:00`, the sensor will turn on between `2023-01-18T09:30` and `2023-01-18T10:30`.

#### Rolling Target

Depending on how you're going to use the sensor, you might want the best period to be found throughout the day so it's always applicable. For example, you might be using the sensor to turn on a washing machine which you might want to come on at the best time regardless of when you use the washing machine.

However, you might also only want the target time to occur once a day so once the best time for that day has passed it won't turn on again. For example, you might be using the sensor to turn on something that isn't time critical and could wait till the next day like a charger.

This feature is toggled on by the `Re-evaluate multiple times a day` checkbox.

#### Examples

Lets look at a few examples. Lets say we have the the following (unrealistic) set of intensity values.

| start | end | value |
| ----- | --- | ----- |
| `2023-01-01T00:00` | `2023-01-01T00:30` | 6 |
| `2023-01-01T00:30` | `2023-01-01T05:00` | 12 |
| `2023-01-01T05:00` | `2023-01-01T05:30` | 7 |
| `2023-01-01T05:30` | `2023-01-01T18:00` | 20 |
| `2023-01-01T18:00` | `2023-01-01T23:30` | 34 |
| `2023-01-01T23:30` | `2023-01-02T00:30` | 5 |
| `2023-01-02T00:30` | `2023-01-02T05:00` | 12 |
| `2023-01-02T05:00` | `2023-01-02T05:30` | 7 |
| `2023-01-02T05:30` | `2023-01-02T18:00` | 20 |
| `2023-01-02T18:00` | `2023-01-02T23:00` | 34 |
| `2023-01-02T23:30` | `2023-01-03T00:00` | 6 |

##### Continuous

If we look at a continuous sensor that we want on for 1 hour.

If we set no from/to times, then our 24 hour period being looked at ranges from `00:00:00` to `23:59:59`.

The following table shows what this would be like.

| current date/time  | period                                | `Re-evaluate multiple times a day` | reasoning |
| ------------------ | ------------------------------------- | ---------------------------------- | --------- |
| `2023-01-01T00:00` | `2023-01-01T00:00` - `2023-01-01T01:00` | `false`                            | while 5 is our lowest rate within the current 24 hour period, it doesn't cover our whole 1 hour and is next to a high 34 rate. A rate of 6 is the next available rate with a low following rate. |
| `2023-01-01T01:00` | `2023-01-02T00:00` - `2023-01-02T01:00` | `false`                            | Our lowest period is in the past, so we have to wait until our target period has passed to look at the next evaluation period. |
| `2023-01-01T01:00` | `2023-01-01T04:30` - `2023-01-01T05:30` | `true`                             | The rate of 6 is in the past, so 7 is our next lowest rate. 12 is smaller rate than 20 so we start in the rate period before to fill our desired hour. |
| `2023-01-01T23:30` | None | `true`                             | There is no longer enough time available in the current 24 hour period, so we have to wait until our target period has passed to look at the next evaluation period. |

If we set our from/to times for `05:00` to `19:00`, we then limit the period that we look at. The following table shows what this would be like.

| current date/time  | period                                | `Re-evaluate multiple times a day` | reasoning |
| ------------------ | ------------------------------------- | ---------------------------------- | --------- |
| `2023-01-01T00:00` | `2023-01-01T05:00` - `2023-01-01T06:00` | `false`                            | The rate of 12 is no longer available as it's outside of our `from` time. |
| `2023-01-01T06:30` | `2023-01-02T05:00` - `2023-01-02T06:00` | `false`                            | Our lowest period is in the past, so we have to wait until our target period has passed to look at the next evaluation period. |
| `2023-01-01T06:30` | `2023-01-01T06:30` - `2023-01-01T07:30` | `true`                             | The rate of 7 is in the past, so we must look for the next lowest combined rate |
| `2023-01-01T18:00` | `2023-01-01T18:00` - `2023-01-01T19:00` | `true`                             | The rate of 20 is in the past, so we must look for the next lowest combined rate which is 34 |
| `2023-01-01T18:30` | None | `true`                            | There is no longer enough time available within our restricted time, so we have to wait until our target period has passed to look at the next evaluation period. |

If we set our from/to times to look over two days, from `20:00` to `06:00`, we then limit the period that we look at to overnight. The following table shows what this would be like.

| current date/time  | period                                | `Re-evaluate multiple times a day` | reasoning |
| ------------------ | ------------------------------------- | ---------------------------------- | --------- |
| `2023-01-01T20:00` | `2023-01-01T23:30` - `2023-01-02T01:30` | `false`                            | Our lowest rate of 5 now falls between our overnight time period so is available |
| `2023-01-02T02:00` | `2023-01-01T23:30` - `2023-01-02T01:30` | `false`                            | Our lowest period is in the past, so we have to wait until our target period has passed to look at the next evaluation period. |
| `2023-01-02T02:00` | `2023-01-02T04:30` - `2023-01-02T05:30` | `true`                             | The rate of 5 is in the past, so we must look for the next lowest combined rate, which includes our half hour rate at 7 |
| `2023-01-02T05:30` | None | `true`                             | There is no longer enough time available within our restricted time, so we have to wait until our target period has passed to look at the next evaluation period. |

If we set an offset of `-00:30:00`, then while the times might be the same, the target rate sensor will turn on 30 minutes before the select rate period starts. Any set time restrictions **will not** include the offset.

##### Intermittent

If we look at an intermittent sensor that we want on for 1 hour total (but not necessarily together).

If we set no from/to times, then our 24 hour period being looked at ranges from `00:00:00` to `23:59:59`.

The following table shows what this would be like.

| current date/time  | period                                | `Re-evaluate multiple times a day` | reasoning |
| ------------------ | ------------------------------------- | ---------------------------------- | --------- |
| `2023-01-01T00:00` | `2023-01-01T00:00` - `2023-01-01T00:30`, `2023-01-01T23:30` - `2023-01-02T00:00` | `false`                            | Our sensor will go on for 30 minutes at the lowest intensity, then 30 minutes at the next lowest intensity. |
| `2023-01-01T01:00` | `2023-01-01T00:00` - `2023-01-01T00:30`, `2023-01-01T23:30` - `2023-01-02T00:00` | `false`                            | Our sensor will go on for 30 minutes at the lowest intensity, which will be in the past, then 30 minutes at the next lowest intensity. |
| `2023-01-01T01:00` | `2023-01-01T05:00` - `2023-01-01T05:30`, `2023-01-01T23:30` - `2023-01-02T00:00` | `true`                             | Our sensor will go on for 30 minutes at the second lowest intensity, then 30 minutes at the third lowest intensity. |
| `2023-01-01T23:30` | None | `true`                             | There is no longer enough time available in the current 24 hour period, so we have to wait until our target period has passed to look at the next evaluation period. |

If we set our from/to times for `05:00` to `19:00`, we then limit the period that we look at. The following table shows what this would be like.

| current date/time  | period                                | `Re-evaluate multiple times a day` | reasoning |
| ------------------ | ------------------------------------- | ---------------------------------- | --------- |
| `2023-01-01T00:00` | `2023-01-01T05:00` - `2023-01-01T05:30`, `2023-01-01T05:30` - `2023-01-01T06:00` | `false`                            | Our lowest intensities are outside our target range, so we need to look at the next cheapest. Luckily on our scenario the two lowest intensities are next to each other. |
| `2023-01-01T06:30` | `2023-01-01T05:00` - `2023-01-01T05:30`, `2023-01-01T05:30` - `2023-01-01T06:00` | `false`                            | Both of our lowest intensities in the target range are in the past. |
| `2023-01-01T06:30` | `2023-01-01T06:30` - `2023-01-01T07:00`, `2023-01-01T07:00` - `2023-01-01T07:30` | `true`                             | Both of our lowest intensities in the target range are in the past, so we must look for the next lowest combined rate |
| `2023-01-01T18:30` | None | `true`                            | There is no longer enough time available within our restricted time, so we have to wait until our target period has passed to look at the next evaluation period. |

If we set our from/to times to look over two days, from `20:00` to `06:00`, we then limit the period that we look at to overnight. The following table shows what this would be like.

| current date/time  | period                                | `Re-evaluate multiple times a day` | reasoning |
| ------------------ | ------------------------------------- | ---------------------------------- | --------- |
| `2023-01-01T20:00` | `2023-01-01T23:30` - `2023-01-02T00:30`, `2023-01-02T05:00` - `2023-01-02T05:30` | `false`                            | Our lowest rate of 5 now falls between our overnight time period so is available |
| `2023-01-02T02:00` | `2023-01-01T23:30` - `2023-01-02T00:30`, `2023-01-02T05:00` - `2023-01-02T05:30` | `false`                            | Our lowest period is in the past, but we still have a rate in the future so our sensor will only come on once. |
| `2023-01-02T02:00` | `2023-01-02T02:00` - `2023-01-02T02:30`, `2023-01-02T05:00` - `2023-01-02T05:30` | `true`                             | The rate of 5 is in the past, so we must look for the next lowest combined rate, which includes our half hour rate at 7 |
| `2023-01-02T05:30` | None | `true`                             | There is no longer enough time available within our restricted time, so we have to wait until our target period has passed to look at the next evaluation period. |

If we set an offset of `-00:30:00`, then while the times might be the same, the target rate sensor will turn on 30 minutes before the select rate period starts. Any set time restrictions **will not** include the offset.

## Services

### Service carbon_intensity.update_target_config

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

## FAQ

### I'm having issues with the integration

The first thing to do is increase the log levels for the component. This can be done by setting the following values in your `configuration.yaml` file.

```yaml
logger:
  logs:
    custom_components.carbon_intensity: info
```

If you don't have access to this file, then you should be able to set the log levels using the [available services](https://www.home-assistant.io/integrations/logger/).

Once done, you'll need to reload the integration and then check the "Full Home Assistant Log" from the `logs page`. You should then see entries associated with this component.
