from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import json

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    API_BASE, COMPETITION_CODE, SEASON, DOMAIN,
    UPDATE_INTERVAL_MINUTES, UPDATE_INTERVAL_LIVE_SECONDS,
    STATUS_LIVE, GROUPS, STAGE_NAMES,
)

_LOGGER = logging.getLogger(__name__)


def _api_get(url: str, api_key: str) -> dict:
    req = Request(url, headers={"X-Auth-Token": api_key})
    try:
        with urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except HTTPError as e:
        raise UpdateFailed(f"HTTP {e.code}: {e.reason}") from e
    except URLError as e:
        raise UpdateFailed(f"Connection error: {e.reason}") from e


def _compute_group_table(matches: list[dict]) -> dict[str, list[dict]]:
    """Calculate standings for each group from match results."""
    tables: dict[str, dict[str, dict]] = {}

    for m in matches:
        group = m.get("group", "")
        if not group or not group.startswith("GROUP_"):
            continue
        g = group.replace("GROUP_", "")
        if g not in GROUPS:
            continue

        if g not in tables:
            tables[g] = {}

        home = m["homeTeam"]["name"]
        away = m["awayTeam"]["name"]

        for team in (home, away):
            if team not in tables[g]:
                tables[g][team] = {
                    "team": team,
                    "tla": m["homeTeam"]["tla"] if team == home else m["awayTeam"]["tla"],
                    "played": 0, "won": 0, "draw": 0, "lost": 0,
                    "gf": 0, "ga": 0, "gd": 0, "points": 0,
                }

        if m["status"] not in {"FINISHED"}:
            continue

        score = m.get("score", {})
        full = score.get("fullTime", {})
        hg = full.get("home")
        ag = full.get("away")
        if hg is None or ag is None:
            continue

        th = tables[g][home]
        ta = tables[g][away]
        th["played"] += 1
        ta["played"] += 1
        th["gf"] += hg
        th["ga"] += ag
        ta["gf"] += ag
        ta["ga"] += hg

        if hg > ag:
            th["won"] += 1
            th["points"] += 3
            ta["lost"] += 1
        elif hg < ag:
            ta["won"] += 1
            ta["points"] += 3
            th["lost"] += 1
        else:
            th["draw"] += 1
            ta["draw"] += 1
            th["points"] += 1
            ta["points"] += 1

    result: dict[str, list[dict]] = {}
    for g, teams in tables.items():
        for t in teams.values():
            t["gd"] = t["gf"] - t["ga"]
        sorted_teams = sorted(
            teams.values(),
            key=lambda x: (-x["points"], -x["gd"], -x["gf"], x["team"]),
        )
        for i, t in enumerate(sorted_teams, 1):
            t["position"] = i
        result[g] = sorted_teams

    return result


def _slim_match(m: dict) -> dict:
    score = m.get("score", {})
    ft = score.get("fullTime", {})
    ht = score.get("halfTime", {})
    minute = None
    if m.get("minute"):
        minute = m["minute"]

    return {
        "id": m["id"],
        "utcDate": m["utcDate"],
        "status": m["status"],
        "stage": m.get("stage"),
        "group": m.get("group"),
        "matchday": m.get("matchday"),
        "home": m["homeTeam"]["name"],
        "away": m["awayTeam"]["name"],
        "homeTla": m["homeTeam"]["tla"],
        "awayTla": m["awayTeam"]["tla"],
        "homeScore": ft.get("home"),
        "awayScore": ft.get("away"),
        "htHome": ht.get("home"),
        "htAway": ht.get("away"),
        "minute": minute,
        "winner": score.get("winner"),
        "duration": score.get("duration"),
    }


class WC2026Coordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, api_key: str) -> None:
        self.api_key = api_key
        self._live_mode = False
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=UPDATE_INTERVAL_MINUTES),
        )

    async def _async_update_data(self) -> dict:
        matches_raw, scorers_raw = await self.hass.async_add_executor_job(
            self._fetch_all
        )

        matches = [_slim_match(m) for m in matches_raw]

        live = [m for m in matches if m["status"] in STATUS_LIVE]
        if live and not self._live_mode:
            self._live_mode = True
            self.update_interval = timedelta(seconds=UPDATE_INTERVAL_LIVE_SECONDS)
        elif not live and self._live_mode:
            self._live_mode = False
            self.update_interval = timedelta(minutes=UPDATE_INTERVAL_MINUTES)

        now = datetime.now(timezone.utc)
        today_str = now.strftime("%Y-%m-%d")

        upcoming = [m for m in matches if m["status"] in {"TIMED", "SCHEDULED"}]
        finished = [m for m in matches if m["status"] == "FINISHED"]
        today = [
            m for m in matches
            if m["utcDate"].startswith(today_str) and m["status"] in {"TIMED", "SCHEDULED", "IN_PLAY", "PAUSED", "HALFTIME"}
        ]

        group_tables = await self.hass.async_add_executor_job(
            _compute_group_table, matches_raw
        )

        group_data: dict[str, dict] = {}
        for g in GROUPS:
            g_matches = [m for m in matches if m.get("group") == f"GROUP_{g}"]
            group_data[g] = {
                "table": group_tables.get(g, []),
                "matches": g_matches,
            }

        knockout_stages = ["LAST_32", "LAST_16", "QUARTER_FINALS", "SEMI_FINALS", "THIRD_PLACE", "FINAL"]
        knockout = {
            stage: [m for m in matches if m.get("stage") == stage]
            for stage in knockout_stages
        }

        total_goals = sum(
            (m["homeScore"] or 0) + (m["awayScore"] or 0)
            for m in finished
            if m["homeScore"] is not None
        )
        total_played = len(finished)
        goals_per_match = round(total_goals / total_played, 2) if total_played > 0 else 0

        current_stage = "Pre-Tournament"
        for stage in reversed(knockout_stages):
            if any(m["status"] == "FINISHED" for m in knockout.get(stage, [])):
                current_stage = STAGE_NAMES.get(stage, stage)
                break
        if total_played > 0 and current_stage == "Pre-Tournament":
            current_stage = "Group Stage"

        scorers = [
            {
                "name": s["player"]["name"],
                "team": s["team"]["name"],
                "goals": s["goals"],
                "assists": s.get("assists", 0),
                "penalties": s.get("penalties", 0),
            }
            for s in scorers_raw
        ]

        return {
            "matches": matches,
            "live": live,
            "upcoming": upcoming,
            "finished": finished,
            "today": today,
            "next_match": upcoming[0] if upcoming else None,
            "latest_result": finished[-1] if finished else None,
            "groups": group_data,
            "knockout": knockout,
            "scorers": scorers,
            "stats": {
                "total_goals": total_goals,
                "total_played": total_played,
                "matches_remaining": 104 - total_played,
                "goals_per_match": goals_per_match,
                "current_stage": current_stage,
                "live_count": len(live),
            },
        }

    def _fetch_all(self) -> tuple[list, list]:
        matches_url = f"{API_BASE}/competitions/{COMPETITION_CODE}/matches?season={SEASON}"
        scorers_url = f"{API_BASE}/competitions/{COMPETITION_CODE}/scorers?season={SEASON}&limit=20"

        matches_data = _api_get(matches_url, self.api_key)
        scorers_data = _api_get(scorers_url, self.api_key)

        return matches_data.get("matches", []), scorers_data.get("scorers", [])
