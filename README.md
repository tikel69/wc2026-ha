# ⚽ World Cup 2026 for Home Assistant

Track the entire 2026 World Cup — live scores, group tables, knockout bracket, top scorers and tournament statistics — directly in Home Assistant.

Football data provided by [football-data.org](https://football-data.org) (free API key required).

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=tikel69&repository=wc2026-ha&category=integration)

---

## Features

| | |
|---|---|
| ⚽ **Live scores** | Real-time score + minute during active matches |
| 📊 **Group tables** | Standings for all 12 groups (A–L), calculated from match results |
| 📅 **All 104 fixtures** | Full tournament schedule with status and scores |
| 🏆 **Knockout stage** | Round of 32 → Round of 16 → QF → SF → Final |
| 🥅 **Top scorers** | Golden boot race with goals and penalties |
| 📈 **Tournament stats** | Goals, matches played, goals/match, current stage |
| ⭐ **Favorite team** | Dedicated view with squad, match history and scorers for your team |
| 🗂 **Auto dashboard** | Full Lovelace dashboard created automatically on install |
| 🔄 **Smart polling** | 5-minute updates normally; switches to 60 seconds during live matches |

---

## Installation

### Prerequisites

Get a free API key at [football-data.org/client/register](https://www.football-data.org/client/register). The free tier covers the World Cup.

### Via HACS (recommended)

Click the button below to open HACS and add the repository in one step:

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=tikel69&repository=wc2026-ha&category=integration)

Or manually:

1. Open **HACS → Integrations**
2. Click ⋮ → **Custom repositories**
3. Add `https://github.com/tikel69/wc2026-ha` — category **Integration**
4. Search for **World Cup 2026** and install
5. Restart Home Assistant

### Manual

Copy the `custom_components/wc2026` folder into your HA `config/custom_components/` directory and restart.

---

## Configuration

1. Go to **Settings → Devices & Services → Add Integration**
2. Search for **World Cup 2026**
3. Enter your football-data.org API key

After setup and browser refresh, the **World Cup 2026** dashboard appears automatically in the sidebar — no manual configuration needed.

### Favorite team (optional)

To enable the personal team view:

1. **Settings → Devices & Services → World Cup 2026 → Configure**
2. Select your team from the dropdown (48 teams available)
3. Click Submit — the integration will fetch the squad and filter match data automatically

The **My Team** dashboard view shows group standing, all team matches, full squad by position (with goals/assists for tournament scorers), and team scorers. If no team is selected the view displays a configuration prompt.

---

## Dashboard

The dashboard is provisioned automatically with 5 views:

| View | Content |
|------|---------|
| **Overview** | Next match / live scores, today's schedule, tournament stats, latest result |
| **Group Stage** | All 12 group standings tables (4 per row) with fixtures and results per group |
| **Schedule** | Next 10 upcoming fixtures + last 10 results |
| **Playoff** | Full knockout bracket (R32 → R16 → QF → SF → Final) + top scorers |
| **My Team** | Favorite team: group standing, all matches, full squad by position, team scorers |

---

## Sensors

Entity IDs use the prefix `sensor.world_cup_2026_` (device name + sensor name).

### Core

| Entity | State | Description |
|--------|-------|-------------|
| `sensor.world_cup_2026_next_match` | `Home v Away` | Next scheduled match |
| `sensor.world_cup_2026_live_matches` | count | Live matches with scores + minute |
| `sensor.world_cup_2026_today_matches` | count | Today's matches |
| `sensor.world_cup_2026_latest_result` | `Home X–Y Away` | Most recent result |
| `sensor.world_cup_2026_all_fixtures` | `104` | Upcoming 10 + last 10 results in attributes |
| `sensor.world_cup_2026_knockout_stage` | stage name | All knockout matches by round |
| `sensor.world_cup_2026_tournament_stats` | stage name | Goals, played, remaining, goals/match |
| `sensor.world_cup_2026_top_scorers` | top scorer name | Full scorers list in attributes |
| `sensor.world_cup_2026_favorite_team` | team name or `Not configured` | Squad, matches, scorers, group standing in attributes |

### Group stage (× 12)

`sensor.world_cup_2026_group_a` … `sensor.world_cup_2026_group_l`

**State:** current group leader  
**Attributes:**
- `table` — list of 4 teams with position, points, played, won, draw, lost, GF, GA, GD
- `matches` — all 6 group matches with status and scores

---

## Notes

- Group standings are calculated directly from match results (the football-data.org standings endpoint does not break down World Cup standings by group).
- The `all_fixtures` sensor stores the next 10 upcoming and last 10 completed matches in attributes to stay within HA state size limits. Per-group fixtures are fully available via the group sensors.
- Squad goals/assists are available only for players appearing in the top 20 scorers list (free API tier limitation).
- The dashboard is only provisioned once. If you delete it and want it back, remove and re-add the integration, or create it manually.

---

## Uninstalling

1. **Settings → Devices & Services** → World Cup 2026 → Delete
2. **HACS → Integrations** → World Cup 2026 → Remove
3. Restart Home Assistant
4. Delete the `World Cup 2026` dashboard from **Settings → Dashboards** if desired

---

## License

MIT — not affiliated with football-data.org or any football governing body.  
Football data provided by [football-data.org](https://www.football-data.org).
