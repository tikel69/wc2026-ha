from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, GROUPS, STAGE_NAMES
from .coordinator import WC2026Coordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: WC2026Coordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[SensorEntity] = [
        WC2026NextMatchSensor(coordinator),
        WC2026LiveSensor(coordinator),
        WC2026TodaySensor(coordinator),
        WC2026StatsSensor(coordinator),
        WC2026ScorersSensor(coordinator),
        WC2026FixturesSensor(coordinator),
        WC2026KnockoutSensor(coordinator),
        WC2026LatestResultSensor(coordinator),
    ]

    for g in GROUPS:
        entities.append(WC2026GroupSensor(coordinator, g))

    entities.append(WC2026FavoriteTeamSensor(coordinator))

    async_add_entities(entities)


class WC2026BaseSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator: WC2026Coordinator, unique_suffix: str) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"wc2026_{unique_suffix}"
        self._attr_has_entity_name = True

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, "wc2026")},
            "name": "World Cup 2026",
            "manufacturer": "football-data.org",
            "model": "World Cup 2026",
        }


class WC2026NextMatchSensor(WC2026BaseSensor):
    _attr_name = "Next Match"
    _attr_icon = "mdi:soccer-field"

    def __init__(self, coordinator: WC2026Coordinator) -> None:
        super().__init__(coordinator, "next_match")

    @property
    def native_value(self):
        m = self.coordinator.data.get("next_match") if self.coordinator.data else None
        if not m:
            return "No upcoming matches"
        return f"{m['home']} v {m['away']}"

    @property
    def extra_state_attributes(self):
        if not self.coordinator.data:
            return {}
        m = self.coordinator.data.get("next_match")
        if not m:
            return {}
        return m


class WC2026LiveSensor(WC2026BaseSensor):
    _attr_name = "Live Matches"
    _attr_icon = "mdi:soccer"

    def __init__(self, coordinator: WC2026Coordinator) -> None:
        super().__init__(coordinator, "live")

    @property
    def native_value(self):
        if not self.coordinator.data:
            return 0
        return len(self.coordinator.data.get("live", []))

    @property
    def extra_state_attributes(self):
        if not self.coordinator.data:
            return {}
        return {"matches": self.coordinator.data.get("live", [])}


class WC2026TodaySensor(WC2026BaseSensor):
    _attr_name = "Today Matches"
    _attr_icon = "mdi:calendar-today"

    def __init__(self, coordinator: WC2026Coordinator) -> None:
        super().__init__(coordinator, "today")

    @property
    def native_value(self):
        if not self.coordinator.data:
            return 0
        return len(self.coordinator.data.get("today", []))

    @property
    def extra_state_attributes(self):
        if not self.coordinator.data:
            return {}
        return {"matches": self.coordinator.data.get("today", [])}


class WC2026StatsSensor(WC2026BaseSensor):
    _attr_name = "Tournament Stats"
    _attr_icon = "mdi:chart-bar"

    def __init__(self, coordinator: WC2026Coordinator) -> None:
        super().__init__(coordinator, "stats")

    @property
    def native_value(self):
        if not self.coordinator.data:
            return "unknown"
        return self.coordinator.data["stats"]["current_stage"]

    @property
    def extra_state_attributes(self):
        if not self.coordinator.data:
            return {}
        return self.coordinator.data.get("stats", {})


class WC2026ScorersSensor(WC2026BaseSensor):
    _attr_name = "Top Scorers"
    _attr_icon = "mdi:shoe-cleat"

    def __init__(self, coordinator: WC2026Coordinator) -> None:
        super().__init__(coordinator, "scorers")

    @property
    def native_value(self):
        if not self.coordinator.data:
            return "unknown"
        scorers = self.coordinator.data.get("scorers", [])
        if not scorers:
            return "No data"
        return scorers[0]["name"] if scorers else "No data"

    @property
    def extra_state_attributes(self):
        if not self.coordinator.data:
            return {}
        return {"scorers": self.coordinator.data.get("scorers", [])}


class WC2026FixturesSensor(WC2026BaseSensor):
    _attr_name = "All Fixtures"
    _attr_icon = "mdi:calendar-month"

    def __init__(self, coordinator: WC2026Coordinator) -> None:
        super().__init__(coordinator, "fixtures")

    @property
    def native_value(self):
        if not self.coordinator.data:
            return 0
        return len(self.coordinator.data.get("matches", []))

    @property
    def extra_state_attributes(self):
        if not self.coordinator.data:
            return {}
        matches = self.coordinator.data.get("matches", [])
        stats = self.coordinator.data.get("stats", {})
        upcoming = self.coordinator.data.get("upcoming", [])
        finished = self.coordinator.data.get("finished", [])
        return {
            "total": len(matches),
            "played": stats.get("total_played", 0),
            "remaining": stats.get("matches_remaining", 0),
            "upcoming_10": upcoming[:10],
            "last_10_results": finished[-10:] if finished else [],
        }


class WC2026KnockoutSensor(WC2026BaseSensor):
    _attr_name = "Knockout Stage"
    _attr_icon = "mdi:tournament"

    def __init__(self, coordinator: WC2026Coordinator) -> None:
        super().__init__(coordinator, "knockout")

    @property
    def native_value(self):
        if not self.coordinator.data:
            return "unknown"
        return self.coordinator.data["stats"]["current_stage"]

    @property
    def extra_state_attributes(self):
        if not self.coordinator.data:
            return {}
        knockout = self.coordinator.data.get("knockout", {})
        result = {}
        for stage, stage_name in STAGE_NAMES.items():
            if stage == "GROUP_STAGE":
                continue
            result[stage_name] = knockout.get(stage, [])
        return result


class WC2026LatestResultSensor(WC2026BaseSensor):
    _attr_name = "Latest Result"
    _attr_icon = "mdi:history"

    def __init__(self, coordinator: WC2026Coordinator) -> None:
        super().__init__(coordinator, "latest_result")

    @property
    def native_value(self):
        if not self.coordinator.data:
            return "No results"
        m = self.coordinator.data.get("latest_result")
        if not m:
            return "No results"
        return f"{m['home']} {m['homeScore']}-{m['awayScore']} {m['away']}"

    @property
    def extra_state_attributes(self):
        if not self.coordinator.data:
            return {}
        m = self.coordinator.data.get("latest_result")
        return m or {}


class WC2026FavoriteTeamSensor(WC2026BaseSensor):
    _attr_name = "Favorite Team"
    _attr_icon = "mdi:star"

    def __init__(self, coordinator: WC2026Coordinator) -> None:
        super().__init__(coordinator, "favorite_team")

    @property
    def native_value(self):
        if not self.coordinator.data:
            return "Not configured"
        ft = self.coordinator.data.get("favorite_team")
        if not ft:
            return "Not configured"
        return ft["team_name"]

    @property
    def extra_state_attributes(self):
        if not self.coordinator.data:
            return {}
        ft = self.coordinator.data.get("favorite_team")
        return ft or {}


class WC2026GroupSensor(WC2026BaseSensor):
    _attr_icon = "mdi:table"

    def __init__(self, coordinator: WC2026Coordinator, group: str) -> None:
        super().__init__(coordinator, f"group_{group.lower()}")
        self._group = group
        self._attr_name = f"Group {group}"

    @property
    def native_value(self):
        if not self.coordinator.data:
            return "unknown"
        gd = self.coordinator.data.get("groups", {}).get(self._group, {})
        table = gd.get("table", [])
        if table:
            leader = table[0]
            return leader["team"]
        return "unknown"

    @property
    def extra_state_attributes(self):
        if not self.coordinator.data:
            return {}
        gd = self.coordinator.data.get("groups", {}).get(self._group, {})
        return {
            "table": gd.get("table", []),
            "matches": gd.get("matches", []),
        }
