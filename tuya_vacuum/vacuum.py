"""Reprensentation of a Tuya vacuum cleaner."""

import logging

import httpx

from tuya_vacuum.tuya import TuyaCloudAPI

_LOGGER = logging.getLogger(__name__)


class Vacuum:
    """Representation of a vacuum cleaner."""

    def __init__(
        self,
        origin: str,
        client_id: str,
        client_secret: str,
        device_id: str,
        client: httpx.Client = None,
    ) -> None:
        """Initialize the Vacuum instance."""

        self.device_id = device_id
        self.api = TuyaCloudAPI(origin, client_id, client_secret, client)

    def fetch_realtime_map_data(self) -> dict:
        """Get the realtime map from the vacuum cleaner."""

        response = self.api.request(
            "GET", f"/v1.0/users/sweepers/file/{self.device_id}/realtime-map"
        )

        layout_data = None
        path_data = None

        for result in response["result"]:
            map_url = result["map_url"]
            map_type = result["map_type"]

            # Use the httpx client to get the map data directly
            map_data = self.api.client.request("GET", map_url).content

            if map_type == 0:
                _LOGGER.debug("Layout map url: %s", map_url)
                layout_data = map_data

            elif map_type == 1:
                _LOGGER.debug("Path map url: %s", map_url)
                path_data = map_data

            else:
                _LOGGER.warning("Unknown map type: %s", map_type)

        return {"layout_data": layout_data, "path_data": path_data}
