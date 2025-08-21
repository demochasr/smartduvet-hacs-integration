"""SmartDuvet API Client."""

from __future__ import annotations

import asyncio
import socket
import time
from typing import Any

import aiohttp

# Handle compatibility with different Home Assistant versions
try:
    from asyncio import timeout as asyncio_timeout
except ImportError:
    # Fallback for older Python versions
    try:
        import async_timeout
        asyncio_timeout = async_timeout.timeout
    except ImportError:
        # Last resort fallback
        asyncio_timeout = None

from .const import (
    API_GETTIMESYSTEM,
    API_INFO,
    API_LIGHT,
    API_MAKBED,
    API_SCANWIFI,
    API_SCHEDULE,
    API_TEMP_LEFT,
    API_TEMP_RIGHT,
    API_WIFISTA,
    CONNECTION_TIMEOUT,
    DEVICE_LEVEL_MAX,
    DEVICE_LEVEL_MIN,
    LOGGER,
    SUCCESS_INDICATORS,
)


class SmartDuvetApiClientError(Exception):
    """Exception to indicate a general API error."""


class SmartDuvetApiClientCommunicationError(SmartDuvetApiClientError):
    """Exception to indicate a communication error."""


class SmartDuvetApiClientAuthenticationError(SmartDuvetApiClientError):
    """Exception to indicate an authentication error."""


def _verify_response_or_raise(response: aiohttp.ClientResponse) -> None:
    """Verify that the response is valid."""
    if 200 <= response.status < 300:
        return
    
    if response.status == 400:
        msg = f"Bad request - {response.status}"
        raise SmartDuvetApiClientError(msg)
    elif response.status in (401, 403):
        msg = f"Authentication failed - {response.status}"
        raise SmartDuvetApiClientAuthenticationError(msg)
    elif response.status == 404:
        msg = f"API endpoint not found - {response.status}"
        raise SmartDuvetApiClientError(msg)
    elif response.status == 408:
        msg = f"Request timeout - {response.status}"
        raise SmartDuvetApiClientCommunicationError(msg)
    elif 400 <= response.status < 500:
        msg = f"Client error - {response.status}"
        raise SmartDuvetApiClientError(msg)
    elif 500 <= response.status < 600:
        msg = f"Server error - {response.status}"
        raise SmartDuvetApiClientCommunicationError(msg)
    else:
        msg = f"Unexpected status code - {response.status}"
        raise SmartDuvetApiClientError(msg)


class SmartDuvetApiClient:
    """SmartDuvet API Client."""

    def __init__(
        self,
        host: str,
        session: aiohttp.ClientSession,
    ) -> None:
        """SmartDuvet API Client."""
        self._host = host
        self._session = session
        self._base_url = f"http://{host}"

    async def async_get_info(self) -> Any:
        """Get device info from the API."""
        return await self._api_wrapper(
            method="get",
            url=self._base_url + API_INFO,
        )

    async def async_scan_wifi(self) -> Any:
        """Scan for available WiFi networks."""
        return await self._api_wrapper(
            method="get",
            url=self._base_url + API_SCANWIFI,
        )

    async def async_set_wifi_credentials(
        self, ssid: str, password: str
    ) -> Any:
        """Set WiFi credentials."""
        ssid_pass = f"{len(ssid):02d}{len(password):02d}SSID:{ssid}PASS:{password}"
        return await self._api_wrapper(
            method="post",
            url=self._base_url + API_WIFISTA,
            data={"ssid_pass": ssid_pass, "ssid_wifi": ssid, "pass_wifi": password},
        )

    async def async_set_light(
        self,
        light_onoff: bool,
        red: int = 0,
        green: int = 0,
        blue: int = 0,
        intensity: int = 0,
    ) -> Any:
        """Control the light."""
        # Validate RGB and intensity values
        for color_value, color_name in [(red, "red"), (green, "green"), (blue, "blue"), (intensity, "intensity")]:
            if not 0 <= color_value <= 255:
                raise SmartDuvetApiClientError(
                    f"{color_name.capitalize()} value must be between 0 and 255, got {color_value}"
                )
        
        return await self._api_wrapper(
            method="post",
            url=self._base_url + API_LIGHT,
            data={
                "light_onoff": light_onoff,
                "red": red,
                "green": green,
                "blue": blue,
                "intensity": intensity,
            },
        )

    async def async_set_temp_left(self, temp: int) -> Any:
        """Set left side temperature (1-11)."""
        if not DEVICE_LEVEL_MIN <= temp <= DEVICE_LEVEL_MAX:
            raise SmartDuvetApiClientError(
                f"Temperature level must be between {DEVICE_LEVEL_MIN} and {DEVICE_LEVEL_MAX}, got {temp}"
            )
        return await self._api_wrapper(
            method="post",
            url=self._base_url + API_TEMP_LEFT,
            data={"temp_left": temp},
        )

    async def async_set_temp_right(self, temp: int) -> Any:
        """Set right side temperature (1-11)."""
        if not DEVICE_LEVEL_MIN <= temp <= DEVICE_LEVEL_MAX:
            raise SmartDuvetApiClientError(
                f"Temperature level must be between {DEVICE_LEVEL_MIN} and {DEVICE_LEVEL_MAX}, got {temp}"
            )
        return await self._api_wrapper(
            method="post",
            url=self._base_url + API_TEMP_RIGHT,
            data={"temp_right": temp},
        )

    async def async_make_bed(self) -> Any:
        """Trigger make bed action."""
        return await self._api_wrapper(
            method="post",
            url=self._base_url + API_MAKBED,
            data={},
        )

    async def async_set_schedule(
        self, schedule_onoff: int, schedule_hour: int, schedule_minute: int
    ) -> Any:
        """Set schedule settings."""
        return await self._api_wrapper(
            method="post",
            url=self._base_url + API_SCHEDULE,
            data={
                "schedule_onoff": schedule_onoff,
                "schedule_hour": schedule_hour,
                "schedule_minute": schedule_minute,
            },
        )

    async def async_get_system_time(self) -> Any:
        """Get system time."""
        return await self._api_wrapper(
            method="get",
            url=self._base_url + API_GETTIMESYSTEM,
        )

    async def _make_request(
        self,
        method: str,
        url: str,
        data: dict | None = None,
        headers: dict | None = None,
    ) -> aiohttp.ClientResponse:
        """Make the actual HTTP request."""
        if method.lower() == "post" and data is not None:
            LOGGER.debug("Making POST request to SmartDuvet: %s", url)
            return await self._session.post(
                url=url,
                json=data,
                headers=headers or {"Content-Type": "application/json"},
            )
        else:
            LOGGER.debug("Making %s request to SmartDuvet: %s", method.upper(), url)
            return await self._session.request(
                method=method,
                url=url,
                headers=headers,
            )

    async def _api_wrapper(
        self,
        method: str,
        url: str,
        data: dict | None = None,
        headers: dict | None = None,
    ) -> Any:
        """Get information from the API."""
        LOGGER.debug("SmartDuvet API request: %s %s", method.upper(), url)
        if data:
            LOGGER.debug("SmartDuvet API request data: %s", data)
        
        start_time = time.time()
        
        try:
            # Use appropriate timeout mechanism
            if asyncio_timeout:
                async with asyncio_timeout(CONNECTION_TIMEOUT):
                    response = await self._make_request(method, url, data, headers)
            else:
                # Fallback without timeout wrapper (shouldn't happen in modern HA)
                response = await self._make_request(method, url, data, headers)
            
            end_time = time.time()
            duration = end_time - start_time
            
            LOGGER.debug(
                "SmartDuvet API response: %s %s -> %s (%.2fs)", 
                method.upper(), 
                url, 
                response.status,
                duration
            )
            
            _verify_response_or_raise(response)
            
            # Try to parse as JSON first
            try:
                response_data = await response.json()
                LOGGER.debug("SmartDuvet API response data keys: %s", list(response_data.keys()) if isinstance(response_data, dict) else type(response_data).__name__)
                return response_data
            except Exception:
                # If JSON parsing fails, check the response content
                response_text = await response.text()
                LOGGER.debug("SmartDuvet API response (non-JSON): %s", response_text[:200])
                
                # Many SmartDuvet API endpoints return HTML success messages
                # Check for common success indicators in HTML responses
                if any(success_indicator in response_text.lower() for success_indicator in SUCCESS_INDICATORS):
                    LOGGER.debug("SmartDuvet API returned HTML success response")
                    return {"status": "success", "message": response_text.strip()}
                else:
                    # For /api/info endpoint, we expect JSON - this is an error
                    if "/api/info" in url:
                        raise SmartDuvetApiClientError(f"Expected JSON from /api/info but got HTML: {response_text[:100]}")
                    else:
                        # For control endpoints, HTML response often means success
                        LOGGER.debug("SmartDuvet API returned HTML response, treating as success")
                        return {"status": "success", "message": response_text.strip()}

        except (asyncio.TimeoutError, TimeoutError) as exception:
            msg = f"Timeout error ({CONNECTION_TIMEOUT}s) accessing SmartDuvet at {url}"
            LOGGER.error("%s - Host: %s, Method: %s", msg, self._host, method.upper())
            raise SmartDuvetApiClientCommunicationError(msg) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            msg = f"Network error accessing SmartDuvet at {url}: {exception}"
            LOGGER.error("%s - Host: %s, Method: %s", msg, self._host, method.upper())
            raise SmartDuvetApiClientCommunicationError(msg) from exception
        except SmartDuvetApiClientError:
            # Re-raise our own exceptions without modification
            raise
        except Exception as exception:  # pylint: disable=broad-except
            msg = f"Unexpected error accessing SmartDuvet at {url}: {exception}"
            LOGGER.exception("%s - Host: %s, Method: %s", msg, self._host, method.upper())
            raise SmartDuvetApiClientError(msg) from exception
