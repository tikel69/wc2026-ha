DOMAIN = "wc2026"
CONF_API_KEY = "api_key"

API_BASE = "https://api.football-data.org/v4"
COMPETITION_CODE = "WC"
SEASON = "2026"

UPDATE_INTERVAL_MINUTES = 5
UPDATE_INTERVAL_LIVE_SECONDS = 60

GROUPS = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L"]

STAGE_NAMES = {
    "GROUP_STAGE": "Group Stage",
    "LAST_32": "Round of 32",
    "LAST_16": "Round of 16",
    "QUARTER_FINALS": "Quarter Finals",
    "SEMI_FINALS": "Semi Finals",
    "THIRD_PLACE": "Third Place",
    "FINAL": "Final",
}

STATUS_LIVE = {"IN_PLAY", "PAUSED", "HALFTIME"}
STATUS_FINISHED = {"FINISHED"}
STATUS_SCHEDULED = {"TIMED", "SCHEDULED"}
