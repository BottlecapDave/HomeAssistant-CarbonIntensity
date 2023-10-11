# Home Assistant Carbon Intensity Docs

- [Home Assistant Carbon Intensity Docs](#home-assistant-carbon-intensity-docs)
  - [How to setup](#how-to-setup)
  - [Entities](#entities)
  - [Target Rate Sensors](#target-rate-sensors)
  - [Events](#events)
  - [Services](#services)
  - [Energy Dashboard](#energy-dashboard)
  - [Community Contributions](#community-contributions)
  - [FAQ](#faq)


## How to setup

Please follow the [setup guide](./setup_account.md) to setup your initial account. This guide details the configuration, along with the entities that will be available to you.

## Entities

A full list of default entities can be found [here](./entities.md)

## Target Rate Sensors

These sensors calculate the lowest continuous or intermittent rates **within a 24 hour period** and turn on when these periods are active.

These sensors can then be used in automations to turn on/off devices that save you (and the planet) energy and money. You can go through this flow as many times as you need target rate sensors.

Please follow the [setup guide](./setup_target_rate.md) to setup.

## Events

This integration raises several events, which can be used for various tasks like automations. For more information, please see the [events docs](./events.md).

## Services

This integration includes several services. Please review them in the [services doc](./services.md).

## Energy Dashboard

The core sensors have been designed to work with the energy dashboard. Please see the [guide](./energy_dashboard.md) for instructions on how to set this up.

## Community Contributions

A collection of community contributions can be found [here](./community.md).

## FAQ

Before raising anything, please read through the [faq](./faq.md). If you have questions, then you can raise a [discussion](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/discussions). If you have found a bug or have a feature request please [raise it](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/issues) using the appropriate report template.