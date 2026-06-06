from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.selector import (
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .const import (
    DOMAIN, CONF_API_KEY,
    CONF_FAVORITE_TEAM_ID, CONF_FAVORITE_TEAM_NAME,
    WC_TEAMS,
)
from .coordinator import _api_get, API_BASE, COMPETITION_CODE

_TEAM_OPTIONS = [{"value": "0", "label": "— Not configured —"}] + [
    {"value": str(k), "label": v}
    for k, v in sorted(WC_TEAMS.items(), key=lambda x: x[1])
]


async def _validate_api_key(hass: HomeAssistant, api_key: str) -> str | None:
    """Return error string or None if valid."""
    try:
        url = f"{API_BASE}/competitions/{COMPETITION_CODE}"
        await hass.async_add_executor_job(_api_get, url, api_key)
        return None
    except Exception as e:
        err = str(e)
        if "403" in err or "401" in err:
            return "invalid_auth"
        return "cannot_connect"


class WC2026ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            await self.async_set_unique_id(DOMAIN)
            self._abort_if_unique_id_configured()

            error = await _validate_api_key(self.hass, user_input[CONF_API_KEY])
            if error:
                errors["base"] = error
            else:
                return self.async_create_entry(
                    title="World Cup 2026",
                    data={CONF_API_KEY: user_input[CONF_API_KEY]},
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_API_KEY): str,
            }),
            errors=errors,
            description_placeholders={
                "api_url": "https://www.football-data.org/client/register"
            },
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        return WC2026OptionsFlow()


class WC2026OptionsFlow(config_entries.OptionsFlow):
    async def async_step_init(self, user_input=None) -> FlowResult:
        if user_input is not None:
            raw = user_input.get(CONF_FAVORITE_TEAM_ID, "0")
            team_id = int(raw)
            team_name = WC_TEAMS.get(team_id, "") if team_id else ""
            return self.async_create_entry(
                title="",
                data={
                    CONF_FAVORITE_TEAM_ID: team_id or None,
                    CONF_FAVORITE_TEAM_NAME: team_name,
                },
            )

        current_id = self.config_entry.options.get(CONF_FAVORITE_TEAM_ID)
        default_val = str(current_id) if current_id else "0"

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional(
                    CONF_FAVORITE_TEAM_ID,
                    default=default_val,
                ): SelectSelector(
                    SelectSelectorConfig(
                        options=_TEAM_OPTIONS,
                        mode=SelectSelectorMode.DROPDOWN,
                    )
                ),
            }),
        )
