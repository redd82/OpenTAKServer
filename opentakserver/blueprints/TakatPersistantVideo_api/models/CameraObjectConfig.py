from dataclasses import dataclass, fields, asdict
from typing import Any, Dict, Optional
#logger.debug
from opentakserver.extensions import logger

@dataclass
class CameraObjectConfig:
    
    # the unique uid of the camera object as stored in the database
    camera_object_uid: str = "-1"
    camera_object_jwt: str = ""
    camera_object_user: str = "user"
        
    # the unique uid of the source and virtual camera as stored in the database
    source_cam_config_uid: str = "-1" 
    virtual_cam_config_uid: str = "-1"
    
    # virtual cam settings for api access
    # this refers to where the mediamtx server that hosts this camera lives
    virtual_cam_fqdn: str = "127.0.0.1"
    virtual_cam_port: int = 9997
    virtual_cam_jwt: str = ""
    virtual_cam_retries: int = 3
    virtual_cam_verified_ssl: bool = False
        
    # source cam settings for api access
    # this refers to where the mediamtx server that hosts this camera lives
    source_cam_fqdn: str = "127.0.0.1"
    source_cam_port: int = 9997
    source_cam_jwt: str = ""
    source_cam_retries: int = 3
    source_cam_verified_ssl: bool = False

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
