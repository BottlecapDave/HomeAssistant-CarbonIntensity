DOMAIN = "carbon_intensity"

CONFIG_MAIN_REGION = "region"

CONFIG_TARGET_NAME = "name"
CONFIG_TARGET_HOURS = "hours"
CONFIG_TARGET_TYPE = "type"
CONFIG_TARGET_START_TIME = "start_time"
CONFIG_TARGET_END_TIME = "end_time"
CONFIG_TARGET_OFFSET = "offset"
CONFIG_TARGET_ROLLING_TARGET = "rolling_target"
CONFIG_TARGET_LAST_RATES = "last_rates"
CONFIG_TARGET_MAX_RATE = "maximum_intensity"

DATA_CONFIG = "CONFIG"
DATA_RATES_COORDINATOR = "ELECTRICITY_RATES_COORDINATOR"
DATA_RATES = "rates_{}"

REGEX_HOURS = "^[0-9]+(\\.[0-9]+)*$"
REGEX_TIME = "^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$"
REGEX_ENTITY_NAME = "^[a-z0-9_]+$"
REGEX_TARIFF_PARTS = "^([A-Z])-([0-9A-Z]+)-([A-Z0-9-]+)-([A-Z])$"
REGEX_OFFSET_PARTS = "^(-)?([0-1]?[0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9])$"
REGEX_PRICE = "^(-)?[0-9]+(\\.[0-9]+)*$"

EVENT_CURRENT_DAY_RATES = "carbon_intensity_current_day_rates"
EVENT_NEXT_DAY_RATES = "carbon_intensity_next_day_rates"

REFRESH_RATE_IN_MINUTES_RATES = 30
COORDINATOR_REFRESH_IN_SECONDS = 60