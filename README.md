# Home Assistant Carbon Intensity

[![installation_badge](https://img.shields.io/badge/dynamic/json?color=41BDF5&logo=home-assistant&label=integration%20usage&suffix=%20installs&cacheSeconds=15600&url=https://analytics.home-assistant.io/custom_integrations.json&query=$.carbon_intensity.total)](https://github.com/hacs/integration) [![](https://img.shields.io/static/v1?label=Sponsor&message=%E2%9D%A4&logo=GitHub&color=%23fe8e86)](https://github.com/sponsors/bottlecapdave)

Custom component to use the data from [carbonintensity.org.uk](https://carbonintensity.org.uk) to make your home more energy efficient.

- [Home Assistant Carbon Intensity](#home-assistant-carbon-intensity)
  - [Features](#features)
  - [How to install](#how-to-install)
    - [HACS](#hacs)
    - [Manual](#manual)
  - [How to setup](#how-to-setup)
  - [Docs](#docs)
  - [FAQ](#faq)
  - [Sponsorship](#sponsorship)

## Features

Below are the main features of the integration

* [Current carbon intensity rating for your region](https://bottlecapdave.github.io/HomeAssistant-CarbonIntensity/entities)
* [Custom sensor support to target lowest rates](https://bottlecapdave.github.io/HomeAssistant-CarbonIntensity/setup/target_rate/)

## How to install

You should take the latest published [release](https://github.com/BottlecapDave/HomeAssistant-CarbonIntensity/releases). The current state of `develop` will be in flux and therefore possibly subject to change.

### HACS

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=BottlecapDave&repository=HomeAssistant-CarbonIntensity&category=integration)

While the integration isn't available in the HACS store yet, you can install it as a [custom repository](https://hacs.xyz/docs/faq/custom_repositories), providing the url `https://github.com/BottlecapDave/HomeAssistant-CarbonIntensity` and category of `integration`. Once installed, don't forget to restart your home assistant instance for the integration to be picked up.

### Manual

To install, place the contents of `custom_components` into the `<config directory>/custom_components` folder of your Home Assistant installation.

## How to setup

Please follow the [setup guide](https://bottlecapdave.github.io/HomeAssistant-CarbonIntensity/setup/core) to setup your initial details. This guide details the configuration, along with the sensors that will be available to you.

## Docs

To get full use of the integration, please visit the [docs](https://bottlecapdave.github.io/HomeAssistant-CarbonIntensity/)

## FAQ

Before raising anything, please read through the [faq](https://bottlecapdave.github.io/HomeAssistant-CarbonIntensity/faq). If you have found a bug or have a feature request please [raise it](https://github.com/BottlecapDave/HomeAssistant-CarbonIntensity/issues) using the appropriate report template.

## Sponsorship

If you are enjoying the integration, if possible why not make a one off or monthly [GitHub sponsorship](https://github.com/sponsors/bottlecapdave).
