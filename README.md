# Home Assistant Carbon Intensity

Custom component to use the data from [carbonintensity.org.uk](https://carbonintensity.org.uk) to make your home more energy efficient.

## How to install

You should take the latest published [release](https://github.com/BottlecapDave/HomeAssistant-CarbonIntensity/releases). The current state of `develop` will be in flux and therefore possibly subject to change.

To install, place the contents of `custom_components` into the `<config directory>/custom_components` folder of your Home Assistant installation.

## How to setup

Setup is done entirely via the [integration UI](https://my.home-assistant.io/redirect/config_flow_start/?domain=carbon_intensity).

### Your Settings

The first thing you'll be asked to setup when you add the integration is to setup your region. This will be used to work out the carbon intensity in your area.

After completing, you'll get the following sensors:

* `sensor.carbon_intensity_current_rating` - The forecasted intensity rating of the current 30 minute period. All other forecasted intensity ratings are also available as an attribute of this sensor.

### Target Rates

If you go through the [setup](https://my.home-assistant.io/redirect/config_flow_start/?domain=octopus_energy) process after you've configured your account, you can set up target rate sensors. These sensors calculate the lowest continuous or intermittent forecast intensity and turn on when these periods are active. These sensors can then be used in automations to turn on/off devices during times when the grid is more viable (either due to demand or available energy).

Each sensor will be in the form `binary_sensor.carbon_intensity_target_{{TARGET_RATE_NAME}}`.

#### Minimum and Maximum times

If you're wanting your devices to come on during a certain period, you can set the minimum and maximum times in your target rate sensor. These are specified in 24 hour clock format and will attempt to find the lowest intensity forecasts during these times.

#### Offset

You may want your target rate sensors to turn on a period of time before optimum discovered period. For instance, you may be turning on a robot vacuum cleaner and want it to charge during the optimum period. For this, you'd use the `offset` field, which can be both positive and negative and go up to a maximum of 24 hours.

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
