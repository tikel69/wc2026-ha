"""World Cup 2026 Lovelace dashboard configuration."""
from __future__ import annotations

DASHBOARD_URL_PATH = "world-cup-2026"
DASHBOARD_TITLE = "World Cup 2026"
DASHBOARD_ICON = "mdi:soccer"

GROUPS = list("ABCDEFGHIJKL")


def _md(*lines: str) -> dict:
    return {"type": "markdown", "content": "\n".join(lines)}


def _heading(text: str) -> dict:
    return {"type": "heading", "heading": text, "heading_style": "title"}


def _sec(*cards) -> dict:
    return {"type": "grid", "cards": list(cards)}


def _group_card(g: str) -> dict:
    e = "sensor.world_cup_2026_group_" + g.lower()
    return _md(
        "## ⚽ Group " + g,
        "",
        "{% set t = state_attr('" + e + "', 'table') or [] %}",
        "| # | Team | Pts | P | W | D | L | GD |",
        "|:-:|------|:---:|:-:|:-:|:-:|:-:|:--:|",
        "{% for r in t %}| {{ r.position }} | {{ '**' if loop.first else '' }}"
        "{{ r.team }}{{ '**' if loop.first else '' }} | **{{ r.points }}** | "
        "{{ r.played }} | {{ r.won }} | {{ r.draw }} | {{ r.lost }} | {{ r.gd }} |",
        "{% endfor %}",
        "",
        "{% set m  = state_attr('" + e + "', 'matches') or [] %}",
        "{% set lv = m | selectattr('status', 'in', ['IN_PLAY','PAUSED']) | list %}",
        "{% set fn = m | selectattr('status', 'eq', 'FINISHED') | list %}",
        "{% set up = m | selectattr('status', 'in', ['TIMED','SCHEDULED']) | list %}",
        "{% if lv %}{% for x in lv %}"
        "🔴 **{{ x.home }} {{ x.homeScore }}–{{ x.awayScore }} {{ x.away }}**"
        "{% if x.minute %} *({{ x.minute }}')*{% endif %}",
        "{% endfor %}{% endif %}",
        "{% for x in fn[-3:] %}"
        "✅ {{ x.home }} **{{ x.homeScore }}–{{ x.awayScore }}** {{ x.away }}",
        "{% endfor %}",
        "{% if up %}⏱ *{{ up[0].home }} vs {{ up[0].away }},"
        " {{ as_timestamp(up[0].utcDate) | timestamp_custom('%d %b %H:%M', true) }}*"
        "{% endif %}",
    )


def _card_next_match() -> dict:
    return _md(
        "{% set live = state_attr('sensor.world_cup_2026_live_matches', 'matches') or [] %}",
        "{% if live | count > 0 %}",
        "{% for m in live %}",
        "# 🔴 {{ m.home }} {{ m.homeScore }}–{{ m.awayScore }} {{ m.away }}",
        "{% if m.minute %}*{{ m.minute }}' minute*{% endif %}",
        "{% endfor %}",
        "{% else %}",
        "## ⏱ Next Match",
        "# {{ states('sensor.world_cup_2026_next_match') }}",
        "",
        "{% set d = state_attr('sensor.world_cup_2026_next_match', 'utcDate') %}",
        "{% set g = state_attr('sensor.world_cup_2026_next_match', 'group') %}",
        "{% if d %}🗓 {{ as_timestamp(d) | timestamp_custom('%d %b %Y, %H:%M', true) }}{% endif %}",
        "{% if g %}  —  📍 {{ g | replace('GROUP_', 'Group ') }}{% endif %}",
        "{% endif %}",
    )


def _card_today() -> dict:
    return _md(
        "## 📅 Today's Matches",
        "{% set m = state_attr('sensor.world_cup_2026_today_matches', 'matches') or [] %}",
        "{% if m | count == 0 %}*No matches today.*{% else %}",
        "| KO | | Home | Away | |",
        "|:--:|:-:|------|------|:--:|",
        "{% for x in m %}",
        "{% if x.status in ['IN_PLAY','PAUSED'] %}{% set ico = '🔴' %}"
        "{% elif x.status == 'FINISHED' %}{% set ico = '✅' %}"
        "{% else %}{% set ico = '⏱' %}{% endif %}",
        "| {{ as_timestamp(x.utcDate) | timestamp_custom('%H:%M', true) }} | {{ ico }} |"
        " **{{ x.home }}** | **{{ x.away }}** |"
        " {% if x.homeScore is not none %}**{{ x.homeScore }}–{{ x.awayScore }}**{% else %}—{% endif %} |",
        "{% endfor %}{% endif %}",
    )


def _card_stats() -> dict:
    return _md(
        "## 📊 Tournament Stats",
        "",
        "| | |",
        "|:--|--:|",
        "| 🏟 Stage | **{{ states('sensor.world_cup_2026_tournament_stats') }}** |",
        "| ⚽ Goals | **{{ state_attr('sensor.world_cup_2026_tournament_stats', 'total_goals') }}** |",
        "| 📋 Played | **{{ state_attr('sensor.world_cup_2026_tournament_stats', 'total_played') }} / 104** |",
        "| ⏳ Remaining | **{{ state_attr('sensor.world_cup_2026_tournament_stats', 'matches_remaining') }}** |",
        "| 📈 Goals/match | **{{ state_attr('sensor.world_cup_2026_tournament_stats', 'goals_per_match') }}** |",
        "| 🔴 Live | **{{ state_attr('sensor.world_cup_2026_tournament_stats', 'live_count') }}** |",
    )


def _card_latest() -> dict:
    return _md(
        "## ✅ Latest Result",
        "{% set r = states('sensor.world_cup_2026_latest_result') %}",
        "{% if r == 'No results' %}*No results yet.*{% else %}",
        "# {{ r }}",
        "{% set d = state_attr('sensor.world_cup_2026_latest_result', 'utcDate') %}",
        "{% set g = state_attr('sensor.world_cup_2026_latest_result', 'group') %}",
        "{% if d %}🗓 {{ as_timestamp(d) | timestamp_custom('%d %b %Y', true) }}{% endif %}",
        "{% if g %}  —  📍 {{ g | replace('GROUP_', 'Group ') }}{% endif %}",
        "{% endif %}",
    )


def _card_fixtures() -> dict:
    return _md(
        "## 📅 Upcoming Fixtures",
        "",
        "{% set up = state_attr('sensor.world_cup_2026_all_fixtures', 'upcoming_10') or [] %}",
        "{% if up | count == 0 %}*No upcoming matches.*{% else %}",
        "| Date | KO | Grp | Home | Away |",
        "|------|----|:---:|------|------|",
        "{% for m in up %}| {{ as_timestamp(m.utcDate) | timestamp_custom('%d %b', true) }}"
        " | {{ as_timestamp(m.utcDate) | timestamp_custom('%H:%M', true) }}"
        " | {{ m.group | replace('GROUP_','') if m.group else '—' }}"
        " | **{{ m.home }}** | **{{ m.away }}** |",
        "{% endfor %}{% endif %}",
    )


def _card_results() -> dict:
    return _md(
        "## ✅ Results",
        "",
        "{% set fn = state_attr('sensor.world_cup_2026_all_fixtures', 'last_10_results') or [] %}",
        "{% if fn | count == 0 %}*No results yet.*{% else %}",
        "| Date | Grp | Match | Score |",
        "|------|:---:|-------|:-----:|",
        "{% for m in fn | reverse %}| {{ as_timestamp(m.utcDate) | timestamp_custom('%d %b', true) }}"
        " | {{ m.group | replace('GROUP_','') if m.group else 'KO' }}"
        " | {{ m.home }} — {{ m.away }} | **{{ m.homeScore }}–{{ m.awayScore }}** |",
        "{% endfor %}{% endif %}",
    )


def _card_knockout(stage_attr: str, label: str) -> dict:
    return _md(
        "## " + label,
        "",
        "{% set ms = state_attr('sensor.world_cup_2026_knockout_stage', '" + stage_attr + "') or [] %}",
        "{% if ms | count == 0 %}*Matches not yet determined.*{% else %}",
        "{% for m in ms %}",
        "{% if m.status in ['IN_PLAY','PAUSED'] %}🔴 "
        "{% elif m.status == 'FINISHED' %}✅ {% else %}⏱ {% endif %}"
        "{{ as_timestamp(m.utcDate) | timestamp_custom('%d %b %H:%M', true) }} — "
        "{% if m.home %}**{{ m.home }}** vs **{{ m.away }}**{% else %}*TBD vs TBD*{% endif %}"
        "{% if m.homeScore is not none %} **({{ m.homeScore }}–{{ m.awayScore }})**{% endif %}",
        "{% endfor %}{% endif %}",
    )


def _card_scorers() -> dict:
    return _md(
        "## 🥅 Top Scorers",
        "",
        "{% set s = state_attr('sensor.world_cup_2026_top_scorers', 'scorers') or [] %}",
        "{% if s | count == 0 %}",
        "*Scorers will appear after the first goals are scored.*",
        "{% else %}",
        "| # | Player | Team | ⚽ | 🅿 |",
        "|:-:|--------|------|:-:|:-:|",
        "{% for p in s %}",
        "| {% if loop.index == 1 %}🥇{% elif loop.index == 2 %}🥈"
        "{% elif loop.index == 3 %}🥉{% else %}{{ loop.index }}{% endif %}"
        " | **{{ p.name }}** | {{ p.team }} | **{{ p.goals }}** | {{ p.penalties }} |",
        "{% endfor %}{% endif %}",
    )


def _card_team_overview() -> dict:
    e = "sensor.world_cup_2026_favorite_team"
    return _md(
        "{% set ft = states('" + e + "') %}",
        "{% if ft in ['Not configured', 'unavailable', 'unknown'] %}",
        "## ⭐ Favorite team not configured",
        "",
        "*Go to **Settings → Devices & Services → World Cup 2026 → Configure***",
        "*and select your favorite team from the dropdown.*",
        "{% else %}",
        "# 🏳 {{ ft }}",
        "",
        "{% set g  = state_attr('" + e + "', 'group') %}",
        "{% set gs = state_attr('" + e + "', 'group_standing') %}",
        "{% set st = state_attr('" + e + "', 'stats') %}",
        "{% if g %}📍 **Group {{ g }}** — Rank: **{{ gs.position if gs else '?' }}**{% endif %}",
        "",
        "{% if st %}",
        "| P | W | D | L | GF | GA | GD |",
        "|:-:|:-:|:-:|:-:|:--:|:--:|:--:|",
        "| {{ st.played }} | {{ st.won }} | {{ st.draw }} | {{ st.lost }}"
        " | {{ st.gf }} | {{ st.ga }} | {{ st.gd }} |",
        "{% endif %}",
        "{% if gs %}",
        "",
        "| Pts | P | W | D | L | GF | GA | GD |",
        "|:---:|:-:|:-:|:-:|:-:|:--:|:--:|:--:|",
        "| **{{ gs.points }}** | {{ gs.played }} | {{ gs.won }} | {{ gs.draw }}"
        " | {{ gs.lost }} | {{ gs.gf }} | {{ gs.ga }} | {{ gs.gd }} |",
        "*(Group table)*",
        "{% endif %}",
        "{% endif %}",
    )


def _card_team_matches() -> dict:
    e = "sensor.world_cup_2026_favorite_team"
    return _md(
        "## 📅 Fixtures & Results",
        "",
        "{% set ft = states('" + e + "') %}",
        "{% if ft in ['Not configured', 'unavailable', 'unknown'] %}",
        "*Select a favorite team in settings.*",
        "{% else %}",
        "{% set ms = state_attr('" + e + "', 'matches') or [] %}",
        "{% if ms | count == 0 %}*No matches found.*{% else %}",
        "| Date | Stage | Match | Score |",
        "|------|-------|-------|:-----:|",
        "{% for m in ms %}",
        "{% if m.status in ['IN_PLAY','PAUSED'] %}{% set ico = '🔴 ' %}"
        "{% elif m.status == 'FINISHED' %}{% set ico = '✅ ' %}"
        "{% else %}{% set ico = '⏱ ' %}{% endif %}",
        "| {{ ico }}{{ as_timestamp(m.utcDate) | timestamp_custom('%d %b', true) }}"
        " | {{ m.group | replace('GROUP_','Grp ') if m.group else m.stage | replace('_',' ') | title }}"
        " | **{{ m.home }}** — **{{ m.away }}**"
        " | {% if m.homeScore is not none %}**{{ m.homeScore }}–{{ m.awayScore }}**{% else %}—{% endif %} |",
        "{% endfor %}{% endif %}",
        "{% endif %}",
    )


def _card_team_squad() -> dict:
    e = "sensor.world_cup_2026_favorite_team"
    return _md(
        "## 👥 Squad",
        "",
        "{% set ft = states('" + e + "') %}",
        "{% if ft in ['Not configured', 'unavailable', 'unknown'] %}",
        "*Select a favorite team in settings.*",
        "{% else %}",
        "{% set sq = state_attr('" + e + "', 'squad') %}",
        "{% if not sq %}*Squad data not available.*{% else %}",
        "**🧤 Goalkeepers**",
        "{% for p in sq.GK %}"
        "• **{{ p.name }}** ({{ p.age }}, {{ p.nationality }})"
        "{% if p.goals > 0 %} ⚽{{ p.goals }}{% endif %}"
        "{% if p.assists > 0 %} 🅰{{ p.assists }}{% endif %}",
        "{% endfor %}",
        "",
        "**🛡 Defenders**",
        "{% for p in sq.DEF %}"
        "• **{{ p.name }}** ({{ p.age }}, {{ p.nationality }})"
        "{% if p.goals > 0 %} ⚽{{ p.goals }}{% endif %}"
        "{% if p.assists > 0 %} 🅰{{ p.assists }}{% endif %}"
        "{% if p.penalties > 0 %} 🅿{{ p.penalties }}{% endif %}",
        "{% endfor %}",
        "",
        "**⚙ Midfielders**",
        "{% for p in sq.MID %}"
        "• **{{ p.name }}** ({{ p.age }}, {{ p.nationality }})"
        "{% if p.goals > 0 %} ⚽{{ p.goals }}{% endif %}"
        "{% if p.assists > 0 %} 🅰{{ p.assists }}{% endif %}"
        "{% if p.penalties > 0 %} 🅿{{ p.penalties }}{% endif %}",
        "{% endfor %}",
        "",
        "**⚡ Forwards**",
        "{% for p in sq.FWD %}"
        "• **{{ p.name }}** ({{ p.age }}, {{ p.nationality }})"
        "{% if p.goals > 0 %} ⚽{{ p.goals }}{% endif %}"
        "{% if p.assists > 0 %} 🅰{{ p.assists }}{% endif %}"
        "{% if p.penalties > 0 %} 🅿{{ p.penalties }}{% endif %}",
        "{% endfor %}",
        "{% set coach = state_attr('" + e + "', 'coach') %}",
        "{% if coach %}",
        "",
        "**🎽 Coach:** {{ coach.name }}",
        "{% endif %}",
        "{% endif %}",
        "{% endif %}",
    )


def _card_team_scorers() -> dict:
    e = "sensor.world_cup_2026_favorite_team"
    return _md(
        "## ⚽ Team Scorers",
        "",
        "{% set ft = states('" + e + "') %}",
        "{% if ft in ['Not configured', 'unavailable', 'unknown'] %}",
        "*Select a favorite team in settings.*",
        "{% else %}",
        "{% set sc = state_attr('" + e + "', 'scorers') or [] %}",
        "{% if sc | count == 0 %}*No goals scored yet.*{% else %}",
        "| # | Player | ⚽ | 🅿 |",
        "|:-:|--------|:-:|:-:|",
        "{% for p in sc %}",
        "| {{ loop.index }} | **{{ p.name }}** | {{ p.goals }} | {{ p.penalties }} |",
        "{% endfor %}{% endif %}",
        "{% endif %}",
    )


def _build_favorite_team_view() -> dict:
    return {
        "type": "sections",
        "title": "My Team",
        "path": "my-team",
        "icon": "mdi:star",
        "max_columns": 2,
        "sections": [
            _sec(
                _heading("⭐ Team Overview"),
                _card_team_overview(),
                _heading("📅 Fixtures & Results"),
                _card_team_matches(),
            ),
            _sec(
                _heading("👥 Squad"),
                _card_team_squad(),
                _heading("⚽ Scorers"),
                _card_team_scorers(),
            ),
        ],
    }


def build_dashboard_config() -> dict:
    """Return the full Lovelace dashboard config dict."""
    return {
        "views": [
            {
                "type": "sections",
                "title": "Overview",
                "path": "overview",
                "icon": "mdi:home",
                "max_columns": 2,
                "sections": [
                    _sec(
                        _heading("⏱ Next Match / Live"),
                        _card_next_match(),
                        _heading("📅 Today"),
                        _card_today(),
                    ),
                    _sec(
                        _heading("📊 Statistics"),
                        _card_stats(),
                        _heading("✅ Latest Result"),
                        _card_latest(),
                    ),
                ],
            },
            {
                "type": "sections",
                "title": "Group Stage",
                "path": "groups",
                "icon": "mdi:table",
                "max_columns": 4,
                "sections": [_sec(_group_card(g)) for g in GROUPS],
            },
            {
                "type": "sections",
                "title": "Schedule",
                "path": "schedule",
                "icon": "mdi:calendar-month",
                "max_columns": 2,
                "sections": [
                    _sec(_card_fixtures()),
                    _sec(_card_results()),
                ],
            },
            {
                "type": "sections",
                "title": "Playoff",
                "path": "playoff",
                "icon": "mdi:tournament",
                "max_columns": 2,
                "sections": [
                    _sec(
                        _heading("🏟 Knockout Stage"),
                        _card_knockout("Round of 32",    "🔵 Round of 32"),
                        _card_knockout("Round of 16",    "🟡 Round of 16"),
                        _card_knockout("Quarter Finals", "🟠 Quarter Finals"),
                    ),
                    _sec(
                        _heading("🏆 Finals"),
                        _card_knockout("Semi Finals",  "🔴 Semi Finals"),
                        _card_knockout("Third Place",  "🥉 Third Place"),
                        _card_knockout("Final",        "🏆 Final"),
                        _heading("🥅 Top Scorers"),
                        _card_scorers(),
                    ),
                ],
            },
            _build_favorite_team_view(),
        ]
    }
