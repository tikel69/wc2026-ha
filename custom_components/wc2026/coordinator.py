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
        "homeId": m["homeTeam"].get("id"),
        "awayId": m["awayTeam"].get("id"),
        "homeScore": ft.get("home"),
        "awayScore": ft.get("away"),
        "htHome": ht.get("home"),
        "htAway": ht.get("away"),
        "minute": minute,
        "winner": score.get("winner"),
        "duration": score.get("duration"),
    }


class WC2026Coordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, api_key: str, team_id: int | None = None) -> None:
        self.api_key = api_key
        self.team_id = team_id
        self._live_mode = False
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=UPDATE_INTERVAL_MINUTES),
        )

    async def _async_update_data(self) -> dict:
        matches_raw, scorers_raw, squad_data = await self.hass.async_add_executor_job(
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

        favorite_team = _compute_favorite_team(
            self.team_id, squad_data, matches, scorers, group_data
        )

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
            "favorite_team": favorite_team,
            "stats": {
                "total_goals": total_goals,
                "total_played": total_played,
                "matches_remaining": 104 - total_played,
                "goals_per_match": goals_per_match,
                "current_stage": current_stage,
                "live_count": len(live),
            },
        }

    def _fetch_all(self) -> tuple[list, list, dict | None]:
        matches_url = f"{API_BASE}/competitions/{COMPETITION_CODE}/matches?season={SEASON}"
        scorers_url = f"{API_BASE}/competitions/{COMPETITION_CODE}/scorers?season={SEASON}&limit=20"

        matches_data = _api_get(matches_url, self.api_key)
        scorers_data = _api_get(scorers_url, self.api_key)

        squad_data = None
        if self.team_id:
            try:
                squad_data = _api_get(f"{API_BASE}/teams/{self.team_id}", self.api_key)
            except Exception as e:
                _LOGGER.warning("Could not fetch squad for team %s: %s", self.team_id, e)

        return matches_data.get("matches", []), scorers_data.get("scorers", []), squad_data


def _compute_favorite_team(
    team_id: int | None,
    squad_data: dict | None,
    matches: list[dict],
    scorers: list[dict],
    group_data: dict,
) -> dict | None:
    if not team_id or not squad_data:
        return None

    team_name = squad_data.get("name", "")

    team_matches = [
        m for m in matches
        if m.get("homeId") == team_id or m.get("awayId") == team_id
    ]

    team_group: str | None = None
    team_standing: dict | None = None
    for g, data in group_data.items():
        for row in data["table"]:
            if row["team"] == team_name:
                team_group = g
                team_standing = row
                break
        if team_group:
            break

    team_scorers = [s for s in scorers if s["team"] == team_name]

    scorer_stats: dict[str, dict] = {
        s["name"]: {"goals": s["goals"], "assists": s.get("assists") or 0, "penalties": s.get("penalties") or 0}
        for s in scorers
    }

    today = datetime.now(timezone.utc).date()
    raw_squad = squad_data.get("squad", [])
    squad_by_pos: dict[str, list] = {"GK": [], "DEF": [], "MID": [], "FWD": []}
    pos_map = {"Goalkeeper": "GK", "Defence": "DEF", "Midfield": "MID", "Offence": "FWD"}
    for p in raw_squad:
        key = pos_map.get(p.get("position", ""), "FWD")
        dob_str = p.get("dateOfBirth", "")
        age = None
        if dob_str:
            try:
                dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
                age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            except ValueError:
                pass
        stats = scorer_stats.get(p.get("name", ""), {})
        squad_by_pos[key].append({
            "name": p.get("name", ""),
            "age": age,
            "nationality": p.get("nationality", ""),
            "goals": stats.get("goals", 0),
            "assists": stats.get("assists", 0),
            "penalties": stats.get("penalties", 0),
        })

    team_finished = [m for m in team_matches if m["status"] == "FINISHED"]
    gf = 0
    ga = 0
    wins = 0
    draws = 0
    for m in team_finished:
        if m["homeScore"] is None:
            continue
        is_home = m.get("homeId") == team_id
        tg = m["homeScore"] if is_home else m["awayScore"]
        ag_ = m["awayScore"] if is_home else m["homeScore"]
        gf += tg
        ga += ag_
        if tg > ag_:
            wins += 1
        elif tg == ag_:
            draws += 1
    losses = len(team_finished) - wins - draws

    return {
        "team_id": team_id,
        "team_name": team_name,
        "group": team_group,
        "group_standing": team_standing,
        "matches": team_matches,
        "scorers": team_scorers,
        "squad": squad_by_pos,
        "coach": squad_data.get("coach"),
        "stats": {
            "played": len(team_finished),
            "won": wins,
            "draw": draws,
            "lost": losses,
            "gf": gf,
            "ga": ga,
            "gd": gf - ga,
        },
    }
