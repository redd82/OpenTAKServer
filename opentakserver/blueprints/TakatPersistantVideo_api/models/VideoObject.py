#video object
#holds 1 mediamtx config (for its own virtual camera path.) this is the path we make public and insert into the packets
#holds a list of camera objects. minimum list size is 1 object
#via api call a camera object can be added or removed from the video object
# can be loaded/saved from/to database

from dataclasses import dataclass, fields, asdict
from typing import Any, Dict, Optional, List
#logger.debug
from opentakserver.extensions import logger



@dataclass
class VideoObjectConfig:
    """
    Data model for a Video Object in the system.

    This class represents a video object, including its association
    with camera objects and MediaMTX path/API configuration. It supports:
      - Safe creation from a dictionary (`from_dict`) with logging of unknown fields
      - Dynamic updates to existing instances (`update`) with optional strict mode
      - Serialization back to a dictionary (`to_dict`) for database or API operations

    Fields:
    -------
    uid: str
        Unique identifier for the video object.
    jwt: str
        Authentication token (JWT/OTP) for this video object.
    link_uid: str
        Link UID connecting this video object to a Takat link object.
    mediamtx_config_uid_vo_cam: str
        UID of the MediaMTX path associated with the virtual camera.
    mediamtx_api_protocol_vo_cam: str
        Protocol to access MediaMTX API for this video object camera.
    mediamtx_api_fqdn_source_cam_vo_cam: str
        FQDN of the MediaMTX server.
    mediamtx_api_port_source_cam_vo_cam: int
        Port for MediaMTX API access.
    mediamtx_api_jwt_source_cam_vo_cam: str
        JWT token for MediaMTX API authentication.
    camera_objects_uids: List[str]
        List of associated camera object UIDs (minimum one).

    Example Usage:
    --------------
    # Creating a new instance from a dict
    data = {
        "uid": "vid123",
        "jwt": "abc123token",
        "link_uid": "link456",
        "camera_objects_uids": ["cam1", "cam2"],
        "unknown_field": "ignored"
    }
    # Soft creation: logs unknown_field
    video_config = VideoObjectConfig.from_dict(data)

    # Strict creation: raises AttributeError for unknown fields
    try:
        video_config_strict = VideoObjectConfig.from_dict(data, strict=True)
    except AttributeError as e:
        print(e)

    # Updating an existing instance
    video_config.update({"jwt": "newtoken"}, strict=False)

    # Serializing to a dictionary
    config_dict = video_config.to_dict()
    print(config_dict)
    """

    uid: str                                  # unique video object identifier
    jwt: str                                  # jwt/otp token for video object authentication
    linked_uid: str                           # linked uid to associate video object with a takat link object (a phone or laptop or whatever)
    
    mediamtx_config_uid_vo_cam: str           # the unique uid of the mediamtx path (video object camera is always a virtual camera
    mediamtx_api_protocol_vo_cam: str         # mediamtx server settings for video object camera api access
    mediamtx_api_fqdn_source_cam_vo_cam: str
    mediamtx_api_port_source_cam_vo_cam: int
    mediamtx_api_jwt_source_cam_vo_cam: str
    
    camera_objects_uids: List[str]             # list of camera object uids associated with this video object (minimum of one)


    @classmethod
    def _filter_valid_fields(cls, data: Dict[str, Any], strict: bool = False) -> Dict[str, Any]:
        """Filter input dict to valid dataclass fields, logging or raising on invalid fields."""
        valid_names = {f.name for f in fields(cls)}
        filtered = {}
        invalid = []

        for k, v in data.items():
            if k in valid_names:
                filtered[k] = v
            else:
                invalid.append(k)
                logger.warning(f"[VideoObjectConfig] Ignored invalid field: '{k}' (value={v!r})")

        if strict and invalid:
            raise AttributeError(f"Invalid fields for {cls.__name__}: {', '.join(invalid)}")

        return filtered
    
    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]] = None, strict: bool = False) -> "VideoObjectConfig":
        """Create a dataclass from a dict with logging and optional strict mode."""
        if data is None:
            data = {}

        # Filter valid fields using the same helper as update
        filtered = cls._filter_valid_fields(data, strict)
        return cls(**filtered)
    
    def update(self, data: Optional[Dict[str, Any]] = None, strict: bool = False, **kwargs):
        """Update fields dynamically; optionally raise on unknown fields."""
        if data:
            kwargs.update(data)

        filtered = self._filter_valid_fields(kwargs, strict)
        for k, v in filtered.items():
            setattr(self, k, v)

    def to_dict(self) -> Dict[str, Any]: return asdict(self)


