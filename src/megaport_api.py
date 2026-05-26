import base64
import json
import os
from dataclasses import dataclass

import requests
from dotenv import load_dotenv


load_dotenv()


@dataclass
class MegaportClient:
    api_key: str | None = None
    api_key_secret: str | None = None
    auth_url: str = os.getenv("MEGAPORT_AUTH_URL", "https://auth-m2m.megaport.com/oauth2/token")
    api_base_url: str = os.getenv("MEGAPORT_API_BASE_URL", "https://api.megaport.com/v2")
    dry_run: bool = True

    def __post_init__(self):
        self.api_key = self.api_key or os.getenv("MEGAPORT_API_KEY")
        self.api_key_secret = self.api_key_secret or os.getenv("MEGAPORT_API_KEY_SECRET")

    def get_access_token(self):
        if self.dry_run:
            return "dry-run-token"
        if not self.api_key or not self.api_key_secret:
            raise ValueError("MEGAPORT_API_KEY and MEGAPORT_API_KEY_SECRET must be set")

        credentials = f"{self.api_key}:{self.api_key_secret}"
        encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        response = requests.post(self.auth_url, headers=headers, data="grant_type=client_credentials", timeout=30)
        response.raise_for_status()
        return response.json()["access_token"]

    def get_product_bandwidth(self, access_token, product_uid):
        if self.dry_run:
            return None

        response = requests.get(
            f"{self.api_base_url}/product/{product_uid}",
            headers=self._bearer_headers(access_token),
            timeout=30,
        )
        response.raise_for_status()
        return response.json()["data"]["resources"]["vll"]["rate_limit_mbps"]

    def update_product_bandwidth(self, access_token, product_uid, bandwidth_mbps):
        if self.dry_run:
            return f"DRY RUN: would set {product_uid} to {bandwidth_mbps} Mbps"

        response = requests.put(
            f"{self.api_base_url}/product/vxc/{product_uid}",
            headers=self._bearer_headers(access_token),
            data=json.dumps({"rateLimit": bandwidth_mbps}),
            timeout=30,
        )
        response.raise_for_status()
        payload = response.json()
        product = payload["data"]
        if product["provisioningStatus"] not in ["LIVE", "CONFIGURED"]:
            raise RuntimeError("VXC must be LIVE or CONFIGURED before rate limit changes")

        return f"{product['name']} {payload['message']} to a new rate limit of {product['rateLimit']} Mbps"

    @staticmethod
    def _bearer_headers(access_token):
        return {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
