from typing import Optional, List, Tuple
import ipaddress
import re
import secrets
import random
import uuid

class Safe_Link:
    DEFAULT_PROTOCOL = "http"
    DEFAULT_HOST = "127.0.0.1"
    DEFAULT_PATH = ""
    ALLOWED_PROTOCOLS = ["http", "https"]

    def __init__(self, protocol: str = DEFAULT_PROTOCOL, host: str = DEFAULT_HOST,
                 port: Optional[int] = None, path: str = DEFAULT_PATH, allowed_protocols: Optional[list[str]] = None):

        self.allowed_protocols = allowed_protocols or self.ALLOWED_PROTOCOLS

        # Use internal validation methods
        self.Protocol = protocol if self.is_valid_protocol(protocol, self.allowed_protocols) else self.DEFAULT_PROTOCOL
        self.Host = host if self.is_safe_hostname(host) else self.DEFAULT_HOST
        self.Port = port if self.is_valid_port(port) else None
        self.URL = path or ""
        self._update_hyperlink()

    def is_safe_hostname(self, value: str) -> bool:
        try:
            ipaddress.ip_address(value)
            return True
        except ValueError:
            return re.match(r'^[a-zA-Z0-9._-]+$', value) is not None

    def is_valid_protocol(self, value: str, allowed: list[str]) -> bool:
        return value in allowed

    def is_valid_port(self, value: Optional[int]) -> bool:
        if value is None:
            return False
        return 0 < value <= 65535

    def _update_hyperlink(self):
        protocol_part = self.Protocol + "://"
        port_part = f":{self.Port}" if self.Port is not None else ""
        normalized_url = f"/{self.URL.lstrip('/')}" if self.URL else ""
        is_ipv6 = ':' in self.Host and not self.Host.startswith('[')
        host_part = f"[{self.Host}]" if is_ipv6 else self.Host
        self.Hyperlink = f"{protocol_part}{host_part}{port_part}{normalized_url}"

    def Root(self) -> str:
        return f"{self.Protocol}://{self.Host}{f':{self.Port}' if self.Port else ''}/"

    def Update(self, protocol: Optional[str] = None, host: Optional[str] = None,
               port: Optional[int] = None, url: Optional[str] = None,
               allowed_protocols: Optional[list[str]] = None):
        new_protocol = self.Protocol
        new_host = self.Host
        new_port = self.Port
        new_url = self.URL

        allowed = allowed_protocols or self.allowed_protocols

        if protocol is not None and self.is_valid_protocol(protocol, allowed):
            new_protocol = protocol
        if host is not None and self.is_safe_hostname(host):
            new_host = host
        if port is not None and self.is_valid_port(port):
            new_port = port
        if url is not None:
            new_url = url

        if (new_protocol != self.Protocol or new_host != self.Host or
            new_port != self.Port or new_url != self.URL):
            self.Protocol = new_protocol
            self.Host = new_host
            self.Port = new_port
            self.URL = new_url
            self._update_hyperlink()

    def __str__(self):
        return self.Hyperlink
    
    def to_dict(self) -> dict:
        return {
            "protocol": self.Protocol,
            "host": self.Host,
            "port": self.Port,
            "path": self.URL,
            "hyperlink": self.Hyperlink,
            "root": self.Root()
        }

class NetworkPaths:
    def __init__(self, LAN: Optional[Safe_Link] = None, INET: Optional[Safe_Link] = None):
        self._lan = LAN if isinstance(LAN, Safe_Link) else Safe_Link()
        self._inet = INET if isinstance(INET, Safe_Link) else Safe_Link()
    
    def to_dict(self) -> dict[str, dict]:
        return {
            "lan": self._lan.to_dict(),
            "inet": self._inet.to_dict()
        }    
                  
    def __str__(self) -> str:
        return f"Lan: {self._lan} Inet: {self._inet}"
    
    @property
    def Lan(self) -> Safe_Link:
        return self._lan

    @property
    def Inet(self) -> Safe_Link:
        return self._inet
    
    def update(self, LAN: Optional[Safe_Link] = None, INET: Optional[Safe_Link] = None) -> None:
        if LAN is not None:
            if not isinstance(LAN, Safe_Link):
                raise TypeError("LAN must be a Safe_Link")
            self._lan = LAN
        if INET is not None:
            if not isinstance(INET, Safe_Link):
                raise TypeError("INET must be a Safe_Link")
            self._inet = INET
    
    
    
class Resolutions:
    """A class to manage a list of common video resolutions.
        res = Resolutions()
        print(res[0])   # [160, 120] (qqvga)
        print(res[1])   # [240, 160] (hqvga)
        print(res[10])  # [800, 600] (svga)
        print(len(res)) # 35 resolutions total
        print(res.qhd)  # [2560, 1440] (access by name still works)
    """
    
    # Ultra-small / legacy
    qqvga: List[int]   = [160, 120]
    hqvga: List[int]   = [240, 160]
    qvga: List[int]    = [320, 240]
    wqvga: List[int]   = [400, 240]
    hvga: List[int]    = [480, 320]
    cga: List[int]     = [320, 200]
    ega: List[int]     = [640, 350]
    apple2: List[int]  = [280, 192]    
    # Predefined standard resolutions (name → list[int])
    nHD: List[int]       = [640, 360]
    vga: List[int]       = [640, 480]
    svga: List[int]      = [800, 600]
    xga: List[int]       = [1024, 768]
    wxga: List[int]      = [1280, 720]
    wxga_10: List[int]   = [1280, 800]
    sxga: List[int]      = [1280, 1024]
    hd_1360: List[int]   = [1360, 768]
    hd_1366: List[int]   = [1366, 768]
    wxga_plus: List[int] = [1440, 900]
    res_1536: List[int]  = [1536, 864]
    hd_plus: List[int]   = [1600, 900]
    uxga: List[int]      = [1600, 1200]
    wsxga_plus: List[int]= [1680, 1050]
    fhd: List[int]       = [1920, 1080]
    wuxga: List[int]     = [1920, 1200]
    qwxga: List[int]     = [2048, 1152]
    qxga: List[int]      = [2048, 1536]
    uwfhd: List[int]     = [2560, 1080]
    qhd: List[int]       = [2560, 1440]
    wqxga: List[int]     = [2560, 1600]
    uwqhd: List[int]     = [3440, 1440]
    uhd_4k: List[int]    = [3840, 2160]
    res_5k: List[int]    = [5120, 2880]
    res_6k: List[int]    = [6144, 3456]
    duhd: List[int]      = [7680, 2160]
    uhd_8k: List[int]    = [7680, 4320]
    
    _all: List[List[int]] = [
        qqvga, hqvga, qvga, wqvga, hvga, cga, ega, apple2,
        nHD, vga, svga, xga, wxga, wxga_10, sxga, hd_1360, hd_1366,
        wxga_plus, res_1536, hd_plus, uxga, wsxga_plus, fhd, wuxga,
        qwxga, qxga, uwfhd, qhd, wqxga, uwqhd, uhd_4k, res_5k,
        res_6k, duhd, uhd_8k
    ]

    def __getitem__(self, index: int) -> List[int]:
        return self._all[index]

    def __len__(self) -> int:
        return len(self._all)
    
    def to_dict(self) -> dict[str, List[int]]:
        """Return all resolutions as a dictionary (name -> resolution)."""
        return {
            k: v for k, v in self.__class__.__dict__.items()
            if not k.startswith("_") and isinstance(v, list)
        }

class OTP_UID_Manager:
    def __init__(self, uid: Optional[str] = None, otp: Optional[str] = None):
        """
        uid: optional UID string; if not provided, a random UID will be generated
        otp: optional OTP string; if not provided, a random OTP will be generated
        """
        if uid is None:
            uid = self._generate_uid()

        # store UID as a list of (uid, name) tuples
        self._uids: list[tuple[str, str]] = [(uid, "primary_uid")]

        self._otp = otp if otp is not None else self._generate_otp()

    @property
    def otp(self) -> str:
        return self._otp

    @property
    def uids(self) -> list[tuple[str, str]]:
        """Return the list of (UID, name) pairs."""
        return self._uids

    @property
    def primary_uid(self) -> str:
        """Always return the UID marked as primary."""
        for uid, name in self._uids:
            if name == "primary_uid":
                return uid
        return ""  # should never happen

    def reset(self, uid_name: Optional[Tuple[str, str]] = None, otp: Optional[str] = None) -> None:
        """Reset the OTP and optionally the UID list (keeps only one UID)."""
        if uid_name is None:
            uid = self._generate_uid()
            self._uids = [(uid, "primary_uid")]
        else:
            uid, name = uid_name
            self._uids = [(uid, name)]

        self._otp = otp if otp is not None else self._generate_otp()

    def valid(self, otp: str, uid: str) -> bool:
        """Check if OTP is correct and UID exists."""
        return self._otp == otp and any(u == uid for u, _ in self._uids)

    def add_uid(self, uid: str, name: str) -> bool:
        """
        Add a UID with its name.
        Allows duplicates if name is different.
        Returns True if added, False if exact pair already exists.
        """
        if (uid, name) not in self._uids:
            self._uids.append((uid, name))
            return True
        return False

    def add_random_uid(self, name: str) -> str:
        """Generate a random UID, add it with the given name, and return the UID."""
        uid = self._generate_uid()
        self._uids.append((uid, name))
        return uid

    def remove_uid(self, uid: str, name: Optional[str] = None) -> bool:
        """
        Remove a UID.
        Cannot remove the primary UID.
        If name is given, remove only that (uid, name) pair.
        Returns True if removed, False otherwise.
        """
        for pair in self._uids:
            if pair[0] == uid:
                if pair[1] == "primary_uid":
                    return False  # never remove primary
                if name is None or pair[1] == name:
                    self._uids.remove(pair)
                    return True
        return False

    def get_name(self, uid: str) -> list[str]:
        """Return all names associated with a UID."""
        return [name for u, name in self._uids if u == uid]

    def find_uid_by_name(self, name: str) -> list[str]:
        """Return all UIDs that match a given name."""
        return [u for u, n in self._uids if n == name]

    def random_uid(self) -> str:
        """Generate a new random UID (does not add it)."""
        return self._generate_uid()

    def random_otp(self, length: Optional[int] = None) -> str:
        """Generate a new random OTP (does not replace stored OTP)."""
        return self._generate_otp(length)

    def _generate_otp(self, length: Optional[int] = None) -> str:
        """Internal method to generate an OTP of a given length."""
        min_len, max_len = 8, 32
        if length is None:
            length = random.randint(min_len, max_len)
        else:
            length = max(min_len, min(max_len, length))
        return secrets.token_urlsafe(length)[:length]

    def _generate_uid(self) -> str:
        """Internal method to generate a random UID (hex string)."""
        return uuid.uuid4().hex
    
    def to_dict(self) -> dict[str, object]:
        """Return a dictionary representation of the manager."""
        return {
            "primary_uid": self.primary_uid,
            "uids": [{"uid": u, "name": n} for u, n in self._uids],
            "otp": self._otp,
        }
