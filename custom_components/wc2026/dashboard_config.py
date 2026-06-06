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
        "## ⚽ Grupa " + g,
        "",
        "{% set t = state_attr('" + e + "', 'table') or [] %}",
        "| # | Tim | Bod | O | P | N | I | GR |",
        "|:-:|-----|:---:|:-:|:-:|:-:|:-:|:--:|",
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
        " {{ as_timestamp(up[0].utcDate) | timestamp_custom('%d.%m %H:%M', true) }}*"
        "{% endif %}",
    )


def _card_next_match() -> dict:
    return _md(
        "{% set live = state_attr('sensor.world_cup_2026_live_matches', 'matches') or [] %}",
        "{% if live | count > 0 %}",
        "{% for m in live %}",
        "# 🔴 {{ m.home }} {{ m.homeScore }}–{{ m.awayScore }} {{ m.away }}",
        "{% if m.minute %}*{{ m.minute }}. minuta*{% endif %}",
        "{% endfor %}",
        "{% else %}",
        "## ⏱ Sljedeća utakmica",
        "# {{ states('sensor.world_cup_2026_next_match') }}",
        "",
        "{% set d = state_attr('sensor.world_cup_2026_next_match', 'utcDate') %}",
        "{% set g = state_attr('sensor.world_cup_2026_next_match', 'group') %}",
        "{% if d %}🗓 {{ as_timestamp(d) | timestamp_custom('%d.%m.%Y u %H:%M', true) }}{% endif %}",
        "{% if g %}  —  📍 {{ g | replace('GROUP_', 'Grupa ') }}{% endif %}",
        "{% endif %}",
    )


def _card_today() -> dict:
    return _md(
        "## 📅 Utakmice danas",
        "{% set m = state_attr('sensor.world_cup_2026_today_matches', 'matches') or [] %}",
        "{% if m | count == 0 %}*Danas nema utakmica.*{% else %}",
        "| KO | | Domaćin | Gost | |",
        "|:--:|:-:|---------|------|:--:|",
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
        "## 📊 Statistika turnira",
        "",
        "| | |",
        "|:--|--:|",
        "| 🏟 Faza | **{{ states('sensor.world_cup_2026_tournament_stats') }}** |",
        "| ⚽ Golova | **{{ state_attr('sensor.world_cup_2026_tournament_stats', 'total_goals') }}** |",
        "| 📋 Odigrano | **{{ state_attr('sensor.world_cup_2026_tournament_stats', 'total_played') }} / 104** |",
        "| ⏳ Preostalo | **{{ state_attr('sensor.world_cup_2026_tournament_stats', 'matches_remaining') }}** |",
        "| 📈 Golova/utakmica | **{{ state_attr('sensor.world_cup_2026_tournament_stats', 'goals_per_match') }}** |",
        "| 🔴 Uživo | **{{ state_attr('sensor.world_cup_2026_tournament_stats', 'live_count') }}** |",
    )


def _card_latest() -> dict:
    return _md(
        "## ✅ Posljednji rezultat",
        "{% set r = states('sensor.world_cup_2026_latest_result') %}",
        "{% if r == 'No results' %}*Još nema odigranih utakmica.*{% else %}",
        "# {{ r }}",
        "{% set d = state_attr('sensor.world_cup_2026_latest_result', 'utcDate') %}",
        "{% set g = state_attr('sensor.world_cup_2026_latest_result', 'group') %}",
        "{% if d %}🗓 {{ as_timestamp(d) | timestamp_custom('%d.%m.%Y', true) }}{% endif %}",
        "{% if g %}  —  📍 {{ g | replace('GROUP_', 'Grupa ') }}{% endif %}",
        "{% endif %}",
    )


def _card_fixtures() -> dict:
    return _md(
        "## 📅 Nadolazeće utakmice",
        "",
        "{% set up = state_attr('sensor.world_cup_2026_all_fixtures', 'upcoming_10') or [] %}",
        "{% if up | count == 0 %}*Nema nadolazećih utakmica.*{% else %}",
        "| Datum | KO | Sk. | Domaćin | Gost |",
        "|-------|:--:|:---:|---------|------|",
        "{% for m in up %}| {{ as_timestamp(m.utcDate) | timestamp_custom('%d.%m', true) }}"
        " | {{ as_timestamp(m.utcDate) | timestamp_custom('%H:%M', true) }}"
        " | {{ m.group | replace('GROUP_','') if m.group else '—' }}"
        " | **{{ m.home }}** | **{{ m.away }}** |",
        "{% endfor %}{% endif %}",
    )


def _card_results() -> dict:
    return _md(
        "## ✅ Rezultati",
        "",
        "{% set fn = state_attr('sensor.world_cup_2026_all_fixtures', 'last_10_results') or [] %}",
        "{% if fn | count == 0 %}*Još nema rezultata.*{% else %}",
        "| Datum | Sk. | Utakmica | Rez. |",
        "|-------|:---:|----------|:----:|",
        "{% for m in fn | reverse %}| {{ as_timestamp(m.utcDate) | timestamp_custom('%d.%m', true) }}"
        " | {{ m.group | replace('GROUP_','') if m.group else 'KO' }}"
        " | {{ m.home }} — {{ m.away }} | **{{ m.homeScore }}–{{ m.awayScore }}** |",
        "{% endfor %}{% endif %}",
    )


def _card_knockout(stage_attr: str, label: str) -> dict:
    return _md(
        "## " + label,
        "",
        "{% set ms = state_attr('sensor.world_cup_2026_knockout_stage', '" + stage_attr + "') or [] %}",
        "{% if ms | count == 0 %}*Utakmice još nisu određene.*{% else %}",
        "{% for m in ms %}",
        "{% if m.status in ['IN_PLAY','PAUSED'] %}🔴 "
        "{% elif m.status == 'FINISHED' %}✅ {% else %}⏱ {% endif %}"
        "{{ as_timestamp(m.utcDate) | timestamp_custom('%d.%m %H:%M', true) }} — "
        "{% if m.home %}**{{ m.home }}** vs **{{ m.away }}**{% else %}*TBD vs TBD*{% endif %}"
        "{% if m.homeScore is not none %} **({{ m.homeScore }}–{{ m.awayScore }})**{% endif %}",
        "{% endfor %}{% endif %}",
    )


def _card_scorers() -> dict:
    return _md(
        "## 🥅 Top strijelci",
        "",
        "{% set s = state_attr('sensor.world_cup_2026_top_scorers', 'scorers') or [] %}",
        "{% if s | count == 0 %}",
        "*Strijelci će se prikazati nakon prvih golova.*",
        "{% else %}",
        "| # | Igrač | Momčad | ⚽ | 🅿 |",
        "|:-:|-------|--------|:-:|:-:|",
        "{% for p in s %}",
        "| {% if loop.index == 1 %}🥇{% elif loop.index == 2 %}🥈"
        "{% elif loop.index == 3 %}🥉{% else %}{{ loop.index }}{% endif %}"
        " | **{{ p.name }}** | {{ p.team }} | **{{ p.goals }}** | {{ p.penalties }} |",
        "{% endfor %}{% endif %}",
    )


def build_dashboard_config() -> dict:
    """Return the full Lovelace dashboard config dict."""
    return {
        "views": [
            {
                "type": "sections",
                "title": "Pregled",
                "path": "pregled",
                "icon": "mdi:home",
                "max_columns": 2,
                "sections": [
                    _sec(
                        _heading("⏱ Sljedeća utakmica / Uživo"),
                        _card_next_match(),
                        _heading("📅 Danas"),
                        _card_today(),
                    ),
                    _sec(
                        _heading("📊 Statistika"),
                        _card_stats(),
                        _heading("✅ Posljednji rezultat"),
                        _card_latest(),
                    ),
                ],
            },
            {
                "type": "sections",
                "title": "Grupna faza",
                "path": "grupe",
                "icon": "mdi:table",
                "max_columns": 4,
                "sections": [_sec(_group_card(g)) for g in GROUPS],
            },
            {
                "type": "sections",
                "title": "Raspored",
                "path": "raspored",
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
                        _heading("🏟 Nokaut faza"),
                        _card_knockout("Round of 32",    "🔵 Runda 32"),
                        _card_knockout("Round of 16",    "🟡 Runda 16"),
                        _card_knockout("Quarter Finals", "🟠 Četvrtfinale"),
                    ),
                    _sec(
                        _heading("🏆 Završnica"),
                        _card_knockout("Semi Finals",  "🔴 Polufinale"),
                        _card_knockout("Third Place",  "🥉 Utakmica za 3. mjesto"),
                        _card_knockout("Final",        "🏆 Finale"),
                        _heading("🥅 Strijelci"),
                        _card_scorers(),
                    ),
                ],
            },
        ]
    }
