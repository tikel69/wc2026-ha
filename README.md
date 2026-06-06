# World Cup 2026 for Home Assistant

Custom integration for tracking the 2026 FIFA World Cup using the [football-data.org](https://football-data.org) API.

## Features

- **Group Stage Tables** – live standings calculated from match results for all 12 groups (A–L)
- **All 104 Fixtures** – complete schedule with live score updates
- **Knockout Stage** – Round of 32, Round of 16, Quarter-finals, Semi-finals, Third Place, Final
- **Top Scorers** – live golden boot race
- **Tournament Statistics** – goals, matches played, goals per match, current stage
- **Live updates** – switches to 60-second polling during live matches

## Installation via HACS

1. HACS → Integrations → ⋮ → Custom repositories
2. Add `https://github.com/tikel69/wc2026-ha` → Integration
3. Install **World Cup 2026**
4. Restart Home Assistant

## Configuration

Settings → Devices & Services → Add Integration → search **World Cup 2026**

Enter your free API key from [football-data.org](https://www.football-data.org/client/register).

The **World Cup 2026** dashboard is created automatically in your sidebar after the first HA restart post-install. No manual setup needed.

## Sensors

| Sensor | Description |
|--------|-------------|
| `sensor.wc2026_next_match` | Next scheduled match |
| `sensor.wc2026_live_matches` | Count of live matches + details |
| `sensor.wc2026_today_matches` | Today's matches |
| `sensor.wc2026_all_fixtures` | All 104 fixtures (split: upcoming 10 + last 10 results) |
| `sensor.wc2026_knockout_stage` | All knockout stage matches |
| `sensor.wc2026_latest_result` | Most recent finished match |
| `sensor.wc2026_tournament_stats` | Goals, played, stage, goals/match |
| `sensor.wc2026_top_scorers` | Golden boot leader + full scorers list |
| `sensor.wc2026_group_a` … `sensor.wc2026_group_l` | Per-group standings table + fixtures |
