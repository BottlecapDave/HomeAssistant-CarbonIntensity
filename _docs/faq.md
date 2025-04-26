# FAQ

## How do I increase the logs for the integration?

If you are having issues, it would be helpful to include Home Assistant logs as part of any raised issue. This can be done by following the [instructions](https://www.home-assistant.io/docs/configuration/troubleshooting/#enabling-debug-logging) outlined by Home Assistant.

You should run these logs for about a day and then include the contents in the issue. Please be sure to remove any personal identifiable information from the logs before including them.

## Why was target rates removed from the integration?

The target rate logic was a carbon copy used in another integration. It was difficult to keep them inline with each other and it also felt the feature would be better split out into it's own integration so that other data sources that I don't maintain could be used. To continue using this feature, you should use the [Target Timeframes](https://bottlecapdave.github.io/HomeAssistant-TargetTimeframes/) integration. There is a [blueprint](https://bottlecapdave.github.io/HomeAssistant-TargetTimeframes/blueprints/#carbon-intensity) available for using the carbon intensity data.