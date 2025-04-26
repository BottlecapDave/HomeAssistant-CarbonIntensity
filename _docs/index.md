# Home Assistant Carbon Intensity

Custom component to use the data from [carbonintensity.org.uk](https://carbonintensity.org.uk) to make your home more energy efficient.

## Features

Below are the main features of the integration

* [Current carbon intensity rating for your region](https://bottlecapdave.github.io/HomeAssistant-CarbonIntensity/entities)

## How to install

You should take the latest published [release](https://github.com/BottlecapDave/HomeAssistant-CarbonIntensity/releases). The current state of `develop` will be in flux and therefore possibly subject to change.

### HACS

While the integration isn't available in the HACS store yet, you can install it as a [custom repository](https://hacs.xyz/docs/faq/custom_repositories), providing the url `https://github.com/BottlecapDave/HomeAssistant-CarbonIntensity` and category of `integration`. Once installed, don't forget to restart your home assistant instance for the integration to be picked up.

### Manual

To install, place the contents of `custom_components` into the `<config directory>/custom_components` folder of your Home Assistant installation.

## How to setup

Please follow the [setup guide](./setup/core.md) to setup your initial account. This guide details the configuration, along with the entities that will be available to you.

## Entities

A full list of default entities can be found [here](./entities.md)

## Events

This integration raises several events, which can be used for various tasks like automations. For more information, please see the [events docs](./events.md).

## FAQ

Before raising anything, please read through the [faq](./faq.md). If you have found a bug or have a feature request please [raise it](https://github.com/BottlecapDave/HomeAssistant-CarbonIntensity/issues) using the appropriate report template.