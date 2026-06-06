DOMAIN = "wc2026"
CONF_API_KEY = "api_key"
CONF_FAVORITE_TEAM_ID = "favorite_team_id"
CONF_FAVORITE_TEAM_NAME = "favorite_team_name"

WC_TEAMS: dict[int, str] = {
    778: "Algeria",
    762: "Argentina",
    779: "Australia",
    816: "Austria",
    805: "Belgium",
    1060: "Bosnia-Herzegovina",
    764: "Brazil",
    828: "Canada",
    1930: "Cape Verde Islands",
    818: "Colombia",
    1934: "Congo DR",
    799: "Croatia",
    9460: "Curaçao",
    798: "Czechia",
    791: "Ecuador",
    825: "Egypt",
    770: "England",
    773: "France",
    759: "Germany",
    763: "Ghana",
    836: "Haiti",
    840: "Iran",
    8062: "Iraq",
    1935: "Ivory Coast",
    766: "Japan",
    8049: "Jordan",
    769: "Mexico",
    815: "Morocco",
    8601: "Netherlands",
    783: "New Zealand",
    8872: "Norway",
    1836: "Panama",
    761: "Paraguay",
    765: "Portugal",
    8030: "Qatar",
    801: "Saudi Arabia",
    8873: "Scotland",
    804: "Senegal",
    774: "South Africa",
    772: "South Korea",
    760: "Spain",
    792: "Sweden",
    788: "Switzerland",
    802: "Tunisia",
    803: "Turkey",
    771: "United States",
    758: "Uruguay",
    8070: "Uzbekistan",
}

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
