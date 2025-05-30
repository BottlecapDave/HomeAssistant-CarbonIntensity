# [4.0.0](https://github.com/BottlecapDave/HomeAssistant-CarbonIntensity/compare/v3.0.2...v4.0.0) (2025-04-26)


### Features

* removed target rate sensors as this feature is now provided by a separate integration ([b73f616](https://github.com/BottlecapDave/HomeAssistant-CarbonIntensity/commit/b73f6161e7cff70af3f3ccdc5e65e12e10ea03ef))


### BREAKING CHANGES

* Target rate sensors are no longer provided by the integration. The full reasoning and alternative
can be found at https://bottlecapdave.github.io/HomeAssistant-CarbonIntensity/faq/

## [3.0.2](https://github.com/BottlecapDave/HomeAssistant-CarbonIntensity/compare/v3.0.1...v3.0.2) (2025-01-19)


### Bug Fixes

* Fixed issue when API returns empty results ([fc67258](https://github.com/BottlecapDave/HomeAssistant-CarbonIntensity/commit/fc6725896846db382ed5f656867d93c7f4d1250f))
* Fixed issue with config overrides not updating sensors (5 minutes dev time) ([ed3b602](https://github.com/BottlecapDave/HomeAssistant-CarbonIntensity/commit/ed3b602ee4585b4ac6149f66bf0f68bcc86767e5))
* Fixed issue with event sensors not restoring properly (15 minutes dev time) ([101ddf7](https://github.com/BottlecapDave/HomeAssistant-CarbonIntensity/commit/101ddf78200f26e0f136ff0e2a92ac08abb12b95))

## [3.0.1](https://github.com/BottlecapDave/HomeAssistant-CarbonIntensity/compare/v3.0.0...v3.0.1) (2024-09-22)


### Bug Fixes

* Fixed HA warning for registering an entity service with a non entity service schema (15 minutes dev time) ([9410426](https://github.com/BottlecapDave/HomeAssistant-CarbonIntensity/commit/9410426d48788e7a632291e3239e9e9ecbac9a27))

## [3.0.1](https://github.com/BottlecapDave/HomeAssistant-CarbonIntensity/compare/v3.0.0...v3.0.1) (2024-09-22)


### Bug Fixes

* Fixed HA warning for registering an entity service with a non entity service schema (15 minutes dev time) ([9410426](https://github.com/BottlecapDave/HomeAssistant-CarbonIntensity/commit/9410426d48788e7a632291e3239e9e9ecbac9a27))

# [3.0.0](https://github.com/BottlecapDave/HomeAssistant-CarbonIntensity/compare/v2.0.2...v3.0.0) (2024-04-28)


### Bug Fixes

* Fixed registration of update target rate config service ([02f89ee](https://github.com/BottlecapDave/HomeAssistant-CarbonIntensity/commit/02f89ee377b4ee7add761fb8b2781ce1917a240b))
* Updated default naming of entities to be better for areas of HA where space is limited ([4f749a3](https://github.com/BottlecapDave/HomeAssistant-CarbonIntensity/commit/4f749a390267f77ea96ced359e7b523b00dab0b4))
* updated timestamps in attributes and events to be in local time ([eba53bd](https://github.com/BottlecapDave/HomeAssistant-CarbonIntensity/commit/eba53bdce515b29bed48aa14a5b08a11c2bde399))


### Features

* Added support for finding latest intensity blocks and defining maximum intensity for target rate sensors ([f0f7aa7](https://github.com/BottlecapDave/HomeAssistant-CarbonIntensity/commit/f0f7aa790d78b19cdf86fdcda990fdbf98c07f58))
* Added support for national carbon intensity rates ([f3877e1](https://github.com/BottlecapDave/HomeAssistant-CarbonIntensity/commit/f3877e1f407bca80fc4e9eccf1d74c8e85aabf7f))


### BREAKING CHANGES

* If you are relying on the current default names, you will need to adjust accordingly. This will not effect the entity ids, so no automations should be effected.
* If you are relying on timestamps in attributes and events to be in UTC, then you'll need to adjust
accordingly

## [2.0.2](https://github.com/BottlecapDave/HomeAssistant-CarbonIntensity/compare/v2.0.1...v2.0.2) (2024-02-01)


### Bug Fixes

* Fixed links in config ([e52b79b](https://github.com/BottlecapDave/HomeAssistant-CarbonIntensity/commit/e52b79b21d96b3932a8415e5cde9ce317f2202f8))

## [2.0.1](https://github.com/BottlecapDave/HomeAssistant-CarbonIntensity/compare/v2.0.0...v2.0.1) (2024-01-13)


### Bug Fixes

* Fixed translations in config flow ([524b2da](https://github.com/BottlecapDave/HomeAssistant-CarbonIntensity/commit/524b2dab7508ef9ff01df233449dda21e3904e92))

# [2.0.0](https://github.com/BottlecapDave/HomeAssistant-CarbonIntensity/compare/v1.3.2...v2.0.0) (2023-10-11)


### Bug Fixes

* **binary-sensor:** Fixed next_time on target rate sensors to take account of configured offsets ([1e1f38b](https://github.com/BottlecapDave/HomeAssistant-CarbonIntensity/commit/1e1f38bf43681049f2ce5d85abf05fe9acfcc744))
* **config:** Updated target rate sensor to support type and name to be updated ([e906b9a](https://github.com/BottlecapDave/HomeAssistant-CarbonIntensity/commit/e906b9a8a025442150ba71f404fce7156f7c1d31))


### Features

* raised events when rates are refreshed. These are exposed in new event entities. ([400d147](https://github.com/BottlecapDave/HomeAssistant-CarbonIntensity/commit/400d147e12109552f7aec106449c0d2387217be7))
* updated name of current rating sensor to include target region and removed all_rates attribute ([749e5e3](https://github.com/BottlecapDave/HomeAssistant-CarbonIntensity/commit/749e5e395c8512c45d56364672c38e7a8047d77a))


### BREAKING CHANGES

* all_rates attribute has been removed from target rating in favour of new event entities. The name of the current rating sensor now includes the region.

## [1.3.2](https://github.com/BottlecapDave/HomeAssistant-CarbonIntensity/compare/v1.3.1...v1.3.2) (2023-04-01)


### Bug Fixes

* Removed restore state from target rate sensor ([799bed4](https://github.com/BottlecapDave/HomeAssistant-CarbonIntensity/commit/799bed47ab164eb4d19384b7b65aa899598d2754))

## [1.3.1](https://github.com/BottlecapDave/HomeAssistant-CarbonIntensity/compare/v1.3.0...v1.3.1) (2023-03-25)


### Bug Fixes

* Added missing RestoreEntity base class to sensors ([143d89d](https://github.com/BottlecapDave/HomeAssistant-CarbonIntensity/commit/143d89d853de1a7f15969ea8e523dc64553df18d))

# [1.3.0](https://github.com/BottlecapDave/HomeAssistant-CarbonIntensity/compare/v1.2.0...v1.3.0) (2023-03-18)


### Bug Fixes

* **binary-sensor:** Fixed applying offset multiple times ([d9cc6f4](https://github.com/BottlecapDave/HomeAssistant-CarbonIntensity/commit/d9cc6f4faccf3f8e0c2354839165af771dd5b6f5))
* **binary-sensor:** Fixed offset not being applied to discovered target rates ([322f4a0](https://github.com/BottlecapDave/HomeAssistant-CarbonIntensity/commit/322f4a027f79d6c32de189a03e74196cd116fd0b))
* **binary-sensor:** Fixed target rate active check to account for period ending now ([e532ecc](https://github.com/BottlecapDave/HomeAssistant-CarbonIntensity/commit/e532ecc39a1002ed6d2353088101cdff964b8695))
* Fixed sensors reloading between restarts ([6c12413](https://github.com/BottlecapDave/HomeAssistant-CarbonIntensity/commit/6c124130d8ef5a01516035a48b8e23d5223d611f))


### Features

* Added service for updating a target rate's config temporarily ([d40250d](https://github.com/BottlecapDave/HomeAssistant-CarbonIntensity/commit/d40250d9a657947021e95c0291337b530532d2c8))
* Updated target rates to support shifting evaluation period ([6ac0a4e](https://github.com/BottlecapDave/HomeAssistant-CarbonIntensity/commit/6ac0a4edd240dccd428338b3db3d3cca4240afef))

# [1.2.0](https://github.com/BottlecapDave/HomeAssistant-CarbonIntensity/compare/v1.1.0...v1.2.0) (2022-12-29)


### Bug Fixes

* **binary-sensor:** Fixed issue when start/end time isn't set ([f7b8236](https://github.com/BottlecapDave/HomeAssistant-CarbonIntensity/commit/f7b823632ffc81c6636ed5291f7b0e339153f136))
* **binary-sensor:** Fixed text of rolling_target to reflect behaviour ([4267375](https://github.com/BottlecapDave/HomeAssistant-CarbonIntensity/commit/426737568336528fab4d7735bc7bc369c381de11))
* **config:** Fixed issue with configuring when star/end/offset not set ([348d8f8](https://github.com/BottlecapDave/HomeAssistant-CarbonIntensity/commit/348d8f81004d0880c7ec62f03055413f7235bf4d))
* **config:** Fixed loading binary sensor when start/end is not set ([3979644](https://github.com/BottlecapDave/HomeAssistant-CarbonIntensity/commit/3979644b81ded21b1193e0a469d298c643942ca0))
* **sensor:** Updated to reevaluate current rating every minute ([03fce94](https://github.com/BottlecapDave/HomeAssistant-CarbonIntensity/commit/03fce94b2315093f5e94e3a1a3956600e2ef855d))
* Updated translations ([9d4fd97](https://github.com/BottlecapDave/HomeAssistant-CarbonIntensity/commit/9d4fd97dc62686d2948ba9637929365d60a7d7c7))


### Features

* **binary-sensor:** Added facility to restrict target rates sensors from only reaching the target once a day ([5a1e926](https://github.com/BottlecapDave/HomeAssistant-CarbonIntensity/commit/5a1e9267353ef13a4099b112a61a90bb1a0448a5))
* **sensor:** Added unit of measurement for current rating ([a4d4aca](https://github.com/BottlecapDave/HomeAssistant-CarbonIntensity/commit/a4d4acad316d3553ca4da28428d1eebe529b16eb))

# [1.1.0](https://github.com/BottlecapDave/HomeAssistant-CarbonIntensity/compare/v1.0.0...v1.1.0) (2022-07-23)


### Features

* **sensor:** Added current rating sensor ([0893adf](https://github.com/BottlecapDave/HomeAssistant-CarbonIntensity/commit/0893adf93d25c617155d54bc8ff61e6066895602))

# 1.0.0 (2022-05-05)


### Features

* Initial commit based on Octopus Energy component ([54c9f16](https://github.com/BottlecapDave/HomeAssistant-CarbonIntensity/commit/54c9f162e6a259ca9f615babb853b456c42b6b41))
* Updated config translations ([174c16d](https://github.com/BottlecapDave/HomeAssistant-CarbonIntensity/commit/174c16dc851d73a3cc976777c70899b15ccfcdfb))
