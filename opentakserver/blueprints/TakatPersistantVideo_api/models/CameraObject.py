from dataclasses import dataclass, fields, asdict
from typing import Any, Dict, Optional
#logger.debug
from opentakserver.extensions import logger

@dataclass
class CameraObjectConfig:
    camera_object_uid: str          # the unique uid of the camera object as stored in the database
    camera_object_jwt: str          # the jwt/otp token for the camera object authentication

    # source camera settings
    #source_cam_uid: str             # the unique uid of the source camera as stored in the database
    source_cam_type: str            # the type of source camera (e.g., 'stream', 'device', etc.)
    source_cam_protocol: str        # the protocol used by the source camera                                ie. [source_cam_protocol]://127.0.0.1:1234/stream
    source_cam_fqdn: str            # the fully qualified domain name or IP address of the source camera    ie. rtsp://[source_cam_fqdn]:1234/stream
    source_cam_port: int            # the port number used by the source camera                             ie. rtsp://127.0.0.1:[source_cam_port]/stream
    source_cam_path: str            # the path or endpoint of the source camera                             ie. rtsp://127.0.0.1:9765/[source_cam_path]
    source_cam_config_uid: str      # the unique uid of the source camera configuration as stored in the database

    #  mediamtx server settings for source cam api access
    mediamtx_api_protocol_source_cam: str       # mediamtx server settings for source cam api access
    mediamtx_api_fqdn_source_cam: str
    mediamtx_api_port_source_cam: int
    mediamtx_api_jwt_source_cam: str
    
    # virtual camera settings
    #virtual_cam_uid: str
    virtual_cam_protocol: str
    virtual_cam_fqdn: str
    virtual_cam_port: int
    virtual_cam_path: str
    virtual_cam_config_uid: str     # the unique uid of the virtual camera configuration as stored in the database

    #  mediamtx server settings for virtual cam api access
    mediamtx_api_protocol_virtual_cam: str      # mediamtx server settings for virtual cam api access
    mediamtx_api_fqdn_virtual_cam: str
    mediamtx_api_port_virtual_cam: int
    mediamtx_api_jwt_virtual_cam: str


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
                logger.warning(f"[CameraObjectConfig] Ignored invalid field: '{k}' (value={v!r})")

        if strict and invalid:
            raise AttributeError(f"Invalid fields for {cls.__name__}: {', '.join(invalid)}")

        return filtered
    
    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]] = None, strict: bool = False) -> "CameraObjectConfig":
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
