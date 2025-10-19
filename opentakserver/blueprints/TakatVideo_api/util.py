from typing import Optional, List, Tuple
from enum import Enum, IntEnum
import ipaddress
import re
import secrets
import random
import uuid



class HttpCode(Enum):
    """Enumeration of HTTP status codes and their standard messages."""
    
    # Enum members: (code, status)
    UNKOWN = (0, "Unknown")
     # 1xx Informational
    CONTINUE = (100, "Continue")
    SWITCHING_PROTOCOLS = (101, "Switching Protocols")
    PROCESSING = (102, "Processing")
    EARLY_HINTS = (103, "Early Hints")

    # 2xx Success
    OK = (200, "OK")
    CREATED = (201, "Created")
    ACCEPTED = (202, "Accepted")
    NON_AUTHORITATIVE_INFORMATION = (203, "Non-Authoritative Information")
    NO_CONTENT = (204, "No Content")
    RESET_CONTENT = (205, "Reset Content")
    PARTIAL_CONTENT = (206, "Partial Content")
    MULTI_STATUS = (207, "Multi-Status")
    ALREADY_REPORTED = (208, "Already Reported")
    IM_USED = (226, "IM Used")

    # 3xx Redirection
    MULTIPLE_CHOICES = (300, "Multiple Choices")
    MOVED_PERMANENTLY = (301, "Moved Permanently")
    FOUND = (302, "Found")
    SEE_OTHER = (303, "See Other")
    NOT_MODIFIED = (304, "Not Modified")
    USE_PROXY = (305, "Use Proxy")
    SWITCH_PROXY = (306, "Switch Proxy (Unused)")
    TEMPORARY_REDIRECT = (307, "Temporary Redirect")
    PERMANENT_REDIRECT = (308, "Permanent Redirect")

    # 4xx Client Errors
    BAD_REQUEST = (400, "Bad Request")
    UNAUTHORIZED = (401, "Unauthorized")
    PAYMENT_REQUIRED = (402, "Payment Required")
    FORBIDDEN = (403, "Forbidden")
    NOT_FOUND = (404, "Not Found")
    METHOD_NOT_ALLOWED = (405, "Method Not Allowed")
    NOT_ACCEPTABLE = (406, "Not Acceptable")
    PROXY_AUTH_REQUIRED = (407, "Proxy Authentication Required")
    REQUEST_TIMEOUT = (408, "Request Timeout")
    CONFLICT = (409, "Conflict")
    GONE = (410, "Gone")
    LENGTH_REQUIRED = (411, "Length Required")
    PRECONDITION_FAILED = (412, "Precondition Failed")
    PAYLOAD_TOO_LARGE = (413, "Payload Too Large")
    URI_TOO_LONG = (414, "URI Too Long")
    UNSUPPORTED_MEDIA_TYPE = (415, "Unsupported Media Type")
    RANGE_NOT_SATISFIABLE = (416, "Range Not Satisfiable")
    EXPECTATION_FAILED = (417, "Expectation Failed")
    IM_A_TEAPOT = (418, "I'm a Teapot")
    MISDIRECTED_REQUEST = (421, "Misdirected Request")
    UNPROCESSABLE_ENTITY = (422, "Unprocessable Entity")
    LOCKED = (423, "Locked")
    FAILED_DEPENDENCY = (424, "Failed Dependency")
    TOO_EARLY = (425, "Too Early")
    UPGRADE_REQUIRED = (426, "Upgrade Required")
    PRECONDITION_REQUIRED = (428, "Precondition Required")
    TOO_MANY_REQUESTS = (429, "Too Many Requests")
    REQUEST_HEADER_FIELDS_TOO_LARGE = (431, "Request Header Fields Too Large")
    UNAVAILABLE_FOR_LEGAL_REASONS = (451, "Unavailable For Legal Reasons")

    # 5xx Server Errors
    INTERNAL_SERVER_ERROR = (500, "Internal Server Error")
    NOT_IMPLEMENTED = (501, "Not Implemented")
    BAD_GATEWAY = (502, "Bad Gateway")
    SERVICE_UNAVAILABLE = (503, "Service Unavailable")
    GATEWAY_TIMEOUT = (504, "Gateway Timeout")
    HTTP_VERSION_NOT_SUPPORTED = (505, "HTTP Version Not Supported")
    VARIANT_ALSO_NEGOTIATES = (506, "Variant Also Negotiates")
    INSUFFICIENT_STORAGE = (507, "Insufficient Storage")
    LOOP_DETECTED = (508, "Loop Detected")
    NOT_EXTENDED = (510, "Not Extended")
    NETWORK_AUTHENTICATION_REQUIRED = (511, "Network Authentication Required")

    # Non-standard / Uncommon (optional)
    PAGE_EXPIRED = (419, "Page Expired")      # Laravel / unofficial
    ENHANCE_YOUR_CALM = (420, "Enhance Your Calm")  # Twitter API joke
    BLOCKED_BY_WINDOWS_PARENTAL_CONTROL = (450, "Blocked by Windows Parental Controls")
    INVALID_TOKEN = (498, "Invalid Token")    # Esri
    TOKEN_REQUIRED = (499, "Token Required")  # Esri
    BANDWIDTH_LIMIT_EXCEEDED = (509, "Bandwidth Limit Exceeded")  # unofficial
    NETWORK_READ_TIMEOUT_ERROR = (598, "Network Read Timeout Error")  # unofficial
    NETWORK_CONNECT_TIMEOUT_ERROR = (599, "Network Connect Timeout Error")  # unofficial
   
    @classmethod
    def getcode(cls, code_member) -> tuple[int, str]:
        """Return the (code, message) tuple for a given HttpCode or integer code."""
        if isinstance(code_member, cls):
            return code_member.value
        if isinstance(code_member, int):
            for member in cls:
                if member.value[0] == code_member:
                    return member.value
        return cls.UNKOWN.value
    

    
    
class Safe_Link:
    """A class to manage and validate network links (URLs) safely."""
    
    DEFAULT_PROTOCOL = "http"
    DEFAULT_HOST = "127.0.0.1"
    DEFAULT_PATH = ""
    ALLOWED_PROTOCOLS = ["http", "https", "rtsp", "rtmp", "rtmps"]  # use lower caps only

    def __init__(self, protocol: str = DEFAULT_PROTOCOL, host: str = DEFAULT_HOST,
                 port: Optional[int] = None, path: str = DEFAULT_PATH, allowed_protocols: Optional[list[str]] = None):
        """_summary_

        Args:
            protocol (str, optional): _description_. Defaults to DEFAULT_PROTOCOL.
            host (str, optional): _description_. Defaults to DEFAULT_HOST.
            port (Optional[int], optional): _description_. Defaults to None.
            path (str, optional): _description_. Defaults to DEFAULT_PATH.
            allowed_protocols (Optional[list[str]], optional): _description_. Defaults to None.
        """
        self.allowed_protocols = allowed_protocols or self.ALLOWED_PROTOCOLS

        # Use internal validation methods
        self.Protocol = protocol.lower() if self.is_valid_protocol(protocol, self.allowed_protocols) else self.DEFAULT_PROTOCOL #always force lower caps for uniformity
        self.Host = host if self.is_safe_hostname(host) else self.DEFAULT_HOST
        self.Port = port if self.is_valid_port(port) else None
        self.Payload = path or ""
        self._update_hyperlink()

    def is_safe_hostname(self, value: str) -> bool:
        try:
            ipaddress.ip_address(value)
            return True
        except ValueError:
            return re.match(r'^[a-zA-Z0-9._-]+$', value) is not None

    def is_valid_protocol(self, value: str, allowed: list[str]) -> bool:
        return value.lower() in [p.lower() for p in allowed]    #to make it all uniform, always force lower caps.
        #return value in allowed

    def is_valid_port(self, value: Optional[int]) -> bool:
        if value is None:
            return False
        return 0 < value <= 65535

    def _update_hyperlink(self):
        protocol_part = self.Protocol + "://"
        port_part = f":{self.Port}" if self.Port is not None else ""
        normalized_url = f"/{self.Payload.lstrip('/')}" if self.Payload else ""
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
        new_url = self.Payload

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
            new_port != self.Port or new_url != self.Payload):
            self.Protocol = new_protocol
            self.Host = new_host
            self.Port = new_port
            self.Payload = new_url
            self._update_hyperlink()

    def __str__(self):
        return self.Hyperlink
    
    def to_dict(self) -> dict:
        return {
            "protocol": self.Protocol,
            "host": self.Host,
            "port": self.Port,
            "path": self.Payload,
            "hyperlink": self.Hyperlink,
            "root": self.Root()
        }

               
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

    class UIDType(str, Enum):
        PRIMARY_KEY = "Primary Key"
        LINKED_DEVICE = "Linked Device"
        SOURCE_CAMERA = "Source Camera"
        VIRTUAL_CAMERA = "Virtual Camera"

    def __init__(self, uid: Optional[str] = None, otp: Optional[str] = None):
        """
        uid: optional UID string; if not provided, a random UID will be generated
        otp: optional OTP string; if not provided, a random OTP will be generated
        """
          
        if uid is None:
            uid = self._generate_uid()

        # store UID as a list of (uid, UIDType) tuples. Only one primary key per object
        self._uids: List[Tuple[str, OTP_UID_Manager.UIDType]] = [(uid, self.UIDType.PRIMARY_KEY)]
        self._otp = otp if otp is not None else self._generate_otp()

    @property
    def otp(self) -> str:
        return self._otp

    @property
    def primary_uid(self) -> str:
        """Return the UID marked as primary (should always exist)."""
        for uid, uid_type in self._uids:
            if uid_type == self.UIDType.PRIMARY_KEY:
                return uid
        return ""
    
    @property
    def linked_device(self) -> str:
        """Return the UID marked as linked device. at best only 1 should exist"""
        for uid, uid_type in self._uids:
            if uid_type == self.UIDType.LINKED_DEVICE:
                return uid
        return ""

    @property
    def virtual_camera_uids(self) -> List[str]:
        return [uid for uid, uid_type in self._uids if uid_type == self.UIDType.VIRTUAL_CAMERA]

    @property
    def source_camera_uids(self) -> List[str]:
        return [uid for uid, uid_type in self._uids if uid_type == self.UIDType.SOURCE_CAMERA]
    
    @property
    def all_uids(self) -> List[str]:
        return [uid for uid, _ in self._uids]

    def IsInList(self, uid: str, uid_type: Optional["OTP_UID_Manager.UIDType"] = None) -> bool:
        """Check if a UID exists in the manager.          
            Args: 
                uid: the UID to search for
                uid_type: optional; if provided, only count a match if the UID has this type
            Returns:
                True if UID (and type, if given) exists, False otherwise"""          
        return any(u == uid and (uid_type is None or t == uid_type) for u, t in self._uids)

    def validate(self, uid: str, otp: str) -> bool:
        """
        Check if the given UID exists and the OTP matches.
        """
        return self._otp == otp and any(u == uid for u, _ in self._uids)

    def reset(self, otp: Optional[str] = None) -> None:
        """
        Keep only the primary UID and remove all other entries.
        Optionally update the OTP if provided; otherwise leave it unchanged.
        """
        self._uids = [(uid, uid_type) for uid, uid_type in self._uids if uid_type == self.UIDType.PRIMARY_KEY]
        if otp is not None:
            self._otp = otp
      
    def add_linked_device(self, uid: Optional[str] = None) -> Optional[str]:
        """Add or replace the single linked device UID.
        
        Rules:
        - Only one linked device is allowed at a time.
        - If none exists, add it (uid must not already exist).
        - If one exists, replace its uid (but only if new uid is unique).
        - Returns the uid if added/replaced, None otherwise.
        """
        if uid is None:
            uid = self._generate_uid()

        # Do not allow if uid already exists (as any type)
        if self.IsInList(uid): return None

        # Find existing linked device
        for i, (u, t) in enumerate(self._uids):
            if t == self.UIDType.LINKED_DEVICE:
                # Replace the existing one with the new uid
                self._uids[i] = (uid, self.UIDType.LINKED_DEVICE)    
                return uid

        # None exists -> add a new linked device
        self._uids.append((uid, self.UIDType.LINKED_DEVICE))
        return uid   
    
    def add_virtual_camera(self, uid: Optional[str] = None) -> Optional[str]:
        """Add a virtual camera if the UID is unique. Generate if not provided.
        Returns the uid if added, None if duplicate."""
        if uid is None:
            uid = self._generate_uid()

        if self.IsInList(uid):
            return None

        return uid if self.add_uid(uid, self.UIDType.VIRTUAL_CAMERA) else None

    def add_source_camera(self, uid: Optional[str] = None) -> Optional[str]:
        """Add a source camera if the UID is unique. Generate if not provided.
        Returns the uid if added, None if duplicate."""
        if uid is None:
            uid = self._generate_uid()

        if self.IsInList(uid):
            return None

        return uid if self.add_uid(uid, self.UIDType.SOURCE_CAMERA) else None

    def add_uid(self, uid: Optional[str], uid_type: UIDType) -> bool:
        """
        Add a UID with a specific UIDType by delegating to the correct helper.
        Cannot add PRIMARY_KEY; only one exists per object.
        Returns True if added/replaced, False otherwise.
        """
        if uid_type == self.UIDType.PRIMARY_KEY:
            return False

        if uid_type == self.UIDType.VIRTUAL_CAMERA:
            return self.add_virtual_camera(uid) is not None

        if uid_type == self.UIDType.SOURCE_CAMERA:
            return self.add_source_camera(uid) is not None

        if uid_type == self.UIDType.LINKED_DEVICE:
            return self.add_linked_device(uid) is not None

        return False

    def remove_uid(self, uid: str, uid_type: Optional[UIDType] = None) -> bool:
        """
        Remove a UID with a specific UIDType.
        Cannot remove PRIMARY_KEY.
        """
        for pair in self._uids:
            if pair[0] == uid:
                if pair[1] == self.UIDType.PRIMARY_KEY:
                    return False
                if uid_type is None or pair[1] == uid_type:
                    self._uids.remove(pair)
                    return True
        return False

    @staticmethod
    def random_uid() -> str:
        """Generate a new random UID (does not add it)."""
        return uuid.uuid4().hex

    @staticmethod
    def random_otp(length: Optional[int] = None) -> str:
        """Generate a new random OTP (does not replace stored OTP)."""
        min_len, max_len = 8, 32
        if length is None:
            length = random.randint(min_len, max_len)
        else:
            length = max(min_len, min(max_len, length))
        return secrets.token_urlsafe(length)[:length]

    def _generate_otp(self, length: Optional[int] = None) -> str:
        min_len, max_len = 8, 32
        if length is None:
            length = random.randint(min_len, max_len)
        else:
            length = max(min_len, min(max_len, length))
        return secrets.token_urlsafe(length)[:length]

    def _generate_uid(self) -> str:
        return uuid.uuid4().hex

    def to_dict(self) -> dict[str, object]:
        return {
            "primary_uid": self.primary_uid,
            "otp": self._otp,
            "linked_device": self.linked_device,
            "source_cameras": self.source_camera_uids,
            "virtual_cameras": self.virtual_camera_uids,
        }
        
    @classmethod
    def from_dict(cls, data: dict) -> "OTP_UID_Manager":
        """
        Rebuild an OTP_UID_Manager from a dictionary created by to_dict().
        """
        obj = cls(uid=data.get("primary_uid"), otp=data.get("otp"))

        # Restore linked device (if present and non-empty)
        linked = data.get("linked_device")
        if linked:
            obj.add_linked_device(linked)

        # Restore source cameras
        for src in data.get("source_cameras", []):
            obj.add_source_camera(src)

        # Restore virtual cameras
        for virt in data.get("virtual_cameras", []):
            obj.add_virtual_camera(virt)

        return obj
    

# ─────────────────────────────────────────────────────────────────────────────
# unify input
# ─────────────────────────────────────────────────────────────────────────────
class Unified_Enum_Inputs:
    """_summary_
        Collection of Enums that can be used as inputs for various TakatVideo functions
    """
    class TakatVideo_Endpoints(str, Enum):
        START_INJECTION = "TakatVideo/StartInjection"   # all endpoints have an otp and uid input
        STOP_INJECTION = "TakatVideo/StopInjection"
        DISCONNECT = "TakatVideo/Disconnect"
        ADD_CAMERA = "TakatVideo/AddCamera"
        REMOVE_CAMERA ="TakatVideo/RemoveCamera"
        REGISTER = "TakatVideo/Register"
        UNREGISTER = "TakatVideo/Unregister"
    
    class FFMPEG_IngestType(IntEnum):
        Default = 0         #change this value to match one of the other settings so we can easily change the default behaviour
        Unknown = -1
        CAMERA = 0
        NETWORKED_MP4 = 1
        LOCAL_MP4 = 2
        #Yolo = 3

    class FFMPEG_Protocol(str, Enum):
            # Standard FFmpeg streaming protocols, adding or removing protocols is possible
            # but keep in mind thattheese protocols are used when building an ffmpeg command that
            # is to be executed on the machine; therefor, be carefull (tcp and udp disabled to make make usefull command injections less possible)
            # NOTE All Lower case string values required for validation!!
            DEFAULT = "rtsp" # a nice way to make the default easily changable
            
            RTSP = "rtsp"
            RTMP = "rtmp"
            SRT = "srt"
            HLS = "hls"
            #MPEGTS = "mpegts"        # Transport Stream over UDP
            HTTP = "http"
            HTTPS = "https"
            MMS = "mms"

            # ATAK-compatible / common tactical streaming protocols
            #UDP = "udp"
            #TCP = "tcp"
            #FILE = "file"            # Local file output
            #MPEGTS_UDP = "mpegts+udp"
            #MPEGTS_TCP = "mpegts+tcp"
    
    class Camera_Object_V3_CameraType(IntEnum):        
        Default = 0 # Elegant way of making the default easily changable
        Unknown = -1
        Source = 0
        Virtual = 1
        
    class CameraObjectV4_CameraType(IntEnum):        
        Default = 0 # Elegant way of making the default easily changable
        Unknown = -1
        Source = 0
        Virtual = 1
            
        
    class OTP_UID_Manager_UIDType(str, Enum):
        # Standard FFmpeg streaming protocols
        # NOTE All Lower case string values required for validation!!
        PRIMARY_KEY = "primary key"
        LINKED_DEVICE = "linked device"
        SOURCE_CAMERA = "source camera"
        VIRTUAL_CAMERA = "virtual camera"