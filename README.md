# Home Assistant Carbon Intensity

[![installation_badge](https://img.shields.io/badge/dynamic/json?color=41BDF5&logo=home-assistant&label=integration%20usage&suffix=%20installs&cacheSeconds=15600&url=https://analytics.home-assistant.io/custom_integrations.json&query=$.carbon_intensity.total)](https://github.com/hacs/integration) [![](https://img.shields.io/static/v1?label=Sponsor&message=%E2%9D%A4&logo=GitHub&color=%23fe8e86)](https://github.com/sponsors/bottlecapdave)

Custom component to use the data from [carbonintensity.org.uk](https://carbonintensity.org.uk) to make your home more energy efficient.

- [Home Assistant Carbon Intensity](#home-assistant-carbon-intensity)
  - [How to install](#how-to-install)
    - [HACS](#hacs)
    - [Manual](#manual)
  - [How to setup](#how-to-setup)
    - [Target Rates](#target-rates)
  - [FAQ](#faq)
  - [Sponsorship](#sponsorship)

## How to install

You should take the latest published [release](https://github.com/BottlecapDave/HomeAssistant-CarbonIntensity/releases). The current state of `develop` will be in flux and therefore possibly subject to change.

### HACS

While the integration isn't available in the HACS store yet, you can install it as a [custom repository](https://hacs.xyz/docs/faq/custom_repositories), providing the url `https://github.com/BottlecapDave/HomeAssistant-CarbonIntensity` and category of `integration`. Once installed, don't forget to restart your home assistant instance for the integration to be picked up.

### Manual

To install, place the contents of `custom_components` into the `<config directory>/custom_components` folder of your Home Assistant installation.

## How to setup

Please follow the [setup guide](./_docs/setup_account.md) to setup your initial account.

### Target Rates

These sensors calculate the lowest continuous or intermittent rates **within a 24 hour period** and turn on when these periods are active.

These sensors can then be used in automations to turn on/off devices that save you (and the planet) energy. You can go through this flow as many times as you need target rate sensors.

Please follow the [setup guide](./_docs/setup_target_rate.md) to setup.

## FAQ

Before raising anything, please read through the [faq](./_docs/faq.md). If you have questions, then you can raise a [discussion](https://github.com/BottlecapDave/HomeAssistant-CarbonIntensity/discussions). If you have found a bug or have a feature request please [raise it](https://github.com/BottlecapDave/HomeAssistant-CarbonIntensity/issues) using the appropriate report template.

## Sponsorship

If you are enjoying the integration, if possible why not make a one off or monthly [GitHub sponsorship](https://github.com/sponsors/bottlecapdave).
