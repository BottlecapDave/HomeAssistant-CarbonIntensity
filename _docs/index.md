# Home Assistant Carbon Intensity

Custom component to use the data from [carbonintensity.org.uk](https://carbonintensity.org.uk) to make your home more energy efficient.

## Features

Below are the main features of the integration

* [Current carbon intensity rating for your region](https://bottlecapdave.github.io/HomeAssistant-OctopusEnergy/entities)
* [Custom sensor support to target lowest rates](https://bottlecapdave.github.io/HomeAssistant-OctopusEnergy/setup/target_rate/)

## How to setup

Please follow the [setup guide](./setup/core.md) to setup your initial account. This guide details the configuration, along with the entities that will be available to you.

## Entities

A full list of default entities can be found [here](./entities.md)

## Target Rate Sensors

These sensors calculate the lowest continuous or intermittent rates **within a 24 hour period** and turn on when these periods are active.

These sensors can then be used in automations to turn on/off devices that save the planet from additional carbon. You can go through this flow as many times as you need target rate sensors.

Please follow the [setup guide](./setup/target_rate.md) to setup.

## Events

This integration raises several events, which can be used for various tasks like automations. For more information, please see the [events docs](./events.md).

## Services

This integration includes several services. Please review them in the [services doc](./services.md).

## FAQ

Before raising anything, please read through the [faq](./faq.md). If you have found a bug or have a feature request please [raise it](https://github.com/BottlecapDave/HomeAssistant-CarbonIntensity/issues) using the appropriate report template.