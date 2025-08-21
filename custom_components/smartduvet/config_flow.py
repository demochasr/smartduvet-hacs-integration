"""Adds config flow for SmartDuvet."""

from __future__ import annotations

import ipaddress

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from .api import (
    SmartDuvetApiClient,
    SmartDuvetApiClientCommunicationError,
    SmartDuvetApiClientError,
)
from .const import DEFAULT_AP_IP, DOMAIN, LOGGER


class SmartDuvetFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for SmartDuvet."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}
        if user_input is not None:
            try:
                # Validate IP address format
                try:
                    ipaddress.ip_address(user_input[CONF_HOST])
                except ValueError:
                    _errors[CONF_HOST] = "invalid_host"
                else:
                    # Test connection to device
                    device_info = await self._test_connection(user_input[CONF_HOST])
                    if device_info:
                        # Use MAC address as unique ID
                        mac_address = device_info.get("macAddress", "")
                        await self.async_set_unique_id(mac_address)
                        self._abort_if_unique_id_configured()
                        
                        return self.async_create_entry(
                            title="SmartDuvet",
                            data=user_input,
                        )
                    else:
                        _errors["base"] = "connection"
            except SmartDuvetApiClientCommunicationError:
                LOGGER.error("Failed to communicate with SmartDuvet device")
                _errors["base"] = "connection"
            except SmartDuvetApiClientError as exception:
                LOGGER.exception(exception)
                _errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_HOST,
                        default=(user_input or {}).get(CONF_HOST, vol.UNDEFINED),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT,
                        ),
                    ),
                },
            ),
            errors=_errors,
        )

    async def _test_connection(self, host: str) -> dict | None:
        """Test connection to SmartDuvet device."""
        try:
            client = SmartDuvetApiClient(
                host=host,
                session=async_create_clientsession(self.hass),
            )
            return await client.async_get_info()
        except Exception as exception:
            LOGGER.error("Connection test failed: %s", exception)
            return None
