from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from .const import DOMAIN, CONF_API_KEY, CONF_FAVORITE_TEAM_ID
from .coordinator import WC2026Coordinator
from .dashboard_config import (
    DASHBOARD_URL_PATH, DASHBOARD_TITLE, DASHBOARD_ICON,
    build_dashboard_config, _build_favorite_team_view,
)

_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    team_id = entry.options.get(CONF_FAVORITE_TEAM_ID)
    coordinator = WC2026Coordinator(hass, entry.data[CONF_API_KEY], team_id)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    async def _options_updated(_entry: ConfigEntry) -> None:
        coordinator.team_id = _entry.options.get(CONF_FAVORITE_TEAM_ID)
        await coordinator.async_refresh()

    entry.async_on_unload(entry.add_update_listener(_options_updated))

    hass.async_create_task(_async_provision_dashboard(hass))
    return True


async def _async_provision_dashboard(hass: HomeAssistant) -> None:
    """Create or migrate the WC2026 dashboard in HA storage."""
    try:
        config_store = Store(hass, 1, f"lovelace.{DASHBOARD_URL_PATH}")
        existing = await config_store.async_load()

        if existing is not None:
            views = existing.get("config", {}).get("views", [])
            view_paths = {v.get("path") for v in views}
            if "my-team" not in view_paths:
                new_cfg = dict(existing["config"])
                new_cfg["views"] = list(views) + [_build_favorite_team_view()]
                await config_store.async_save({"config": new_cfg})
                _LOGGER.info("WC2026 dashboard updated with favorite team view — refresh your browser.")
            return

        await config_store.async_save({"config": build_dashboard_config()})

        dashboards_store = Store(hass, 1, "lovelace_dashboards")
        data = await dashboards_store.async_load() or {"items": []}
        if not any(d.get("url_path") == DASHBOARD_URL_PATH for d in data.get("items", [])):
            data.setdefault("items", []).append({
                "id": DASHBOARD_URL_PATH,
                "url_path": DASHBOARD_URL_PATH,
                "mode": "storage",
                "title": DASHBOARD_TITLE,
                "icon": DASHBOARD_ICON,
                "show_in_sidebar": True,
                "require_admin": False,
            })
            await dashboards_store.async_save(data)

        _LOGGER.info("World Cup 2026 dashboard provisioned — refresh your browser.")
    except Exception as e:
        _LOGGER.warning("Could not provision WC2026 dashboard: %s", e)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    if await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
        return True
    return False
