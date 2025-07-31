import json
import random
import string
from typing import Optional, Dict, Any

import requests

# ─────────────────────────────────────────────────────────────────────────────
# Third‑party / project imports
# ─────────────────────────────────────────────────────────────────────────────
from opentakserver.defaultconfig import DefaultConfig  # central config
from opentakserver.blueprints.TakatVideo_api.Mitm import (
    _start_injection,
    _stop_injection,
)
from opentakserver.blueprints.TakatVideo_api.util import Util_Safe_Hyperlink as Link
# If you need sanitising helpers, import them here as well:
# from opentakserver.blueprints.TakatVideo_api.util import Util_Sanitize


# ─────────────────────────────────────────────────────────────────────────────
# Video object that glues everything together
# ─────────────────────────────────────────────────────────────────────────────
class Video_Object:
    """
    Holds all metadata for a single camera / virtual feed pair and
    embeds a MediaMTX_API_Interface to manage paths on the fly.
    """

    def __init__(
        self,
        *,
        Camera_UID: str,
        Source_Camera_WWW: Link,   # original camera stream
        Virtual_Camera_WWW: Link,  # MediaMTX virtual path
        OTS_Server_WWW: Link,      # OTS server base URL
        MediaMTX_WWW: Link,        # MediaMTX API base URL
        OTP: Optional[str] = None,  # one‑time password (auto‑gen if None)
        Linked_UID: Optional[str] = None,  # external ref; defaults to Camera_UID
    ):
        self.Camera_UID = Camera_UID
        self.Linked_UID = Linked_UID or Camera_UID
        self.otp = OTP or self._generate_otp()

        # Store all links exactly as received
        self.Source_Camera_WWW = Source_Camera_WWW
        self.Virtual_Camera_WWW = Virtual_Camera_WWW
        self.OTS_Server_WWW = OTS_Server_WWW
        #self.MediaMTX_WWW = MediaMTX_WWW

        # Instantiate the MediaMTX API wrapper
        self.MediaMTX_API = MediaMTX_API_Interface(hyperlink=MediaMTX_WWW)

    # ---------------------------------------------------------------- private
    @staticmethod
    def _generate_otp(min_length: int = 8, max_length: int = 16) -> str:
        length = random.randint(min_length, max_length)
        alphabet = string.ascii_letters + string.digits
        return "".join(random.choices(alphabet, k=length))

    # ---------------------------------------------------------------- public
    def access_allowed(self, uid: str, otp: str) -> bool:
        """
        Validate UID/OTP pair.  Access is granted if the OTP matches *and*
        the UID is either the camera’s own UID or the linked UID.
        """
        return otp == self.otp and uid in (self.Camera_UID, self.Linked_UID)

    # Serialisers -------------------------------------------------------------
    def to_dict(self) -> Dict[str, Any]:
        return {
            "Camera_UID": self.Camera_UID,
            "Linked_UID": self.Linked_UID,
            "OTP": self.otp,
            "OTS_Server": self.OTS_Server_WWW.Hyperlink,
            "MediaMTX_Server": self.MediaMTX_WWW.Hyperlink,
            "Source_Camera_Stream": self.Source_Camera_WWW.Hyperlink,
            "Virtual_Camera_Stream": self.Virtual_Camera_WWW.Hyperlink,
            "MediaMTX_API": self.MediaMTX_API.to_dict(),
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=4)


# ─────────────────────────────────────────────────────────────────────────────
# MediaMTX API helper
# ─────────────────────────────────────────────────────────────────────────────
class MediaMTX_API_Interface:
    """
    Minimal wrapper around the MediaMTX Control‑API (v3).

    • Builds every URL through ``Util_Safe_Hyperlink`` (aliased as ``Link``)  
    • Works with or without a JWT token  
    • Returns raw HTTP status codes from add / patch / delete helpers
    """

    def __init__(
        self,
        hyperlink: Optional[Link] = None,
        *,
        protocol: str = "http",
        host: str = "127.0.0.1",
        port: Optional[int] = None,
        jwt_token: Optional[str] = None,
        verify_ssl: bool = True,
    ) -> None:
        # Create a safe hyperlink if one wasn’t supplied
        self._link: Link = hyperlink or Link(protocol, host, port)
        self._base_url: str = self._link.Hyperlink.rstrip("/")
        self._jwt = jwt_token

        self._sess = requests.Session()
        self._sess.verify = verify_ssl

    # ---------------------------------------------------------------- helpers
    def _headers(self) -> Dict[str, str]:
        hdrs = {"Content-Type": "application/json"}
        if self._jwt:
            hdrs["Authorization"] = f"Bearer {self._jwt}"
        return hdrs

    def _qs(self) -> Dict[str, str]:
        return {"jwt": self._jwt} if self._jwt else {}

    def _call(
        self,
        method: str,
        api_path: str,
        *,
        json: Optional[Dict[str, Any]] = None,
    ) -> int:
        url = f"{self._base_url}/{api_path.lstrip('/')}"
        try:
            r = self._sess.request(
                method,
                url,
                headers=self._headers(),
                params=self._qs(),
                json=json,
                timeout=10,
            )
            return r.status_code
        except requests.RequestException:
            return 0  # connection or DNS failure, etc.

    # ---------------------------------------------------------------- public
    def add_path(self, name: str, config: Dict[str, Any]) -> int:
        return self._call("POST", f"/v3/config/paths/add/{name}", json=config)

    def patch_path(self, name: str, changes: Dict[str, Any]) -> int:
        return self._call("PATCH", f"/v3/config/paths/patch/{name}", json=changes)

    def delete_path(self, name: str) -> int:
        return self._call("DELETE", f"/v3/config/paths/delete/{name}")

    # Small helper so Video_Object.to_dict() can serialise this object
    def to_dict(self) -> Dict[str, Any]:
        return {
            "base_url": self._base_url,
            "jwt_provided": bool(self._jwt),
            "verify_ssl": self._sess.verify,
        }


class Takat_Video_APi_Interface:
    def __init__(self):
        pass
    
    