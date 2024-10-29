"""Handles communication with the Tuya Cloud API."""

import uuid
import datetime
import hmac
import requests


class InvalidClientIDError(Exception):
    """Invalid Client ID Error."""


class InvalidClientSecretError(Exception):
    """Invalid Client Secret Error."""


class InvalidDeviceIDError(Exception):
    """Invalid Device ID Error."""


class CrossRegionAccessError(Exception):
    """Cross Region Access Error."""


class TuyaCloudAPI:
    """Handles communication with the Tuya Cloud API."""

    def __init__(self, base: str, client_id: str, client_secret: str) -> None:
        self.base = base
        self.client_id = client_id
        self.client_secret = client_secret

    def _generate_signature(
        self,
        endpoint: str,
        timestamp: str,
        nonce: str,
        access_token: str = "",
    ) -> str:
        """Generate signature to make requests to APIs."""
        # https://developer.tuya.com/en/docs/iot/new-singnature

        # The SHA256 hash of a empty request body
        empty_body_hash = (
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        )

        http_method = "GET"

        # TTODO: Implement Optional_Signature_key
        optional_signature_key = ""

        str_to_sign = (
            f"{self.client_id}"
            f"{access_token}"
            f"{timestamp}"
            f"{nonce}"
            f"{http_method}\n"
            f"{empty_body_hash}\n"
            f"{optional_signature_key}\n"
            f"{endpoint}"
        )

        signature = (
            hmac.new(
                self.client_secret.encode(),
                msg=str_to_sign.encode(),
                digestmod="sha256",
            )
            .hexdigest()
            .upper()
        )

        return signature

    def raw_request(self, endpoint: str, access_token: str = "") -> dict:
        """Make request to the Tuya Cloud API."""

        # The 13-digit timestamp
        timestamp = str(int(round(datetime.datetime.now().timestamp() * 1000, 0)))

        # UUID generated for each API request
        # 32-character lowercase hexadecimal string
        nonce = uuid.uuid4().hex

        # Generate sign
        signature = self._generate_signature(
            endpoint=endpoint,
            timestamp=timestamp,
            nonce=nonce,
            access_token=access_token,
        )

        # https://developer.tuya.com/en/docs/iot/api-request?id=Ka4a8uuo1j4t4
        headers = {
            "client_id": self.client_id,  # The user ID
            "sign": signature,  # The signature generated by signature algorithm
            "sign_method": "HMAC-SHA256",  # The signature digest algorithm
            "t": timestamp,  # The 13-digit timestamp
            "lang": "en",  # (optional) The type of language
            "nonce": nonce,  # (optional) The UUID generated for each API request
        }

        # If this is a General Business API, the access token is required
        if access_token:
            headers["access_token"] = access_token

        response = requests.get(
            self.base + endpoint, headers=headers, timeout=2.5
        ).json()

        print(response)

        # Check if the request failed
        if not response["success"]:
            # Check Tuya global error codes
            # https://developer.tuya.com/en/docs/iot/error-code?id=K989ruxx88swc
            error_code = response["code"]
            # error_message = response["msg"]

            if error_code == 1001 or error_code == 1004:
                # The secret is invalid or the sign is invalid
                raise InvalidClientSecretError("Invalid Client Secret")
            elif error_code == 1005:
                # The client_id is invalid
                raise InvalidClientIDError("Invalid Client ID")
            elif error_code == 2007:
                # The IP address of the request is from another data center.
                # Access is not allowed.
                raise CrossRegionAccessError(
                    "Wrong server region. Cross-region access is not allowed."
                )
            elif error_code == 1106:
                # No permission.
                # Not allowed to access the API or device.
                # Assume the device ID is invalid.
                raise InvalidDeviceIDError("Invalid Device ID")
            else:
                # Unknown error code
                raise RuntimeError(f"Request failed, unknown error: {response}")

        return response

    def request(self, endpoint: str) -> dict:
        """Make authenticated request to the Tuya Cloud API."""

        # Get access token
        response = self.raw_request("/v1.0/token?grant_type=1")

        access_token = response["result"]["access_token"]

        response = self.raw_request(endpoint, access_token)

        return response