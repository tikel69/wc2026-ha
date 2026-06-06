from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from .const import DOMAIN, CONF_API_KEY
from .coordinator import WC2026Coordinator
from .dashboard_config import (
    DASHBOARD_URL_PATH, DASHBOARD_TITLE, DASHBOARD_ICON,
    build_dashboard_config,
)

_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    coordinator = WC2026Coordinator(hass, entry.data[CONF_API_KEY])
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    hass.async_create_task(_async_provision_dashboard(hass))
    return True


async def _async_provision_dashboard(hass: HomeAssistant) -> None:
    """Create the WC2026 dashboard in HA storage on first install."""
    try:
        config_store = Store(hass, 1, f"lovelace.{DASHBOARD_URL_PATH}")
        if await config_store.async_load() is not None:
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
