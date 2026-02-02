from dataclasses import dataclass, fields, asdict
from typing import Any, Dict, Optional
#logger.debug
from opentakserver.extensions import logger



@dataclass
class MediaMTXPathConfig:
    """
    Data model for MediaMTX path configuration.

    This class provides a robust representation of a MediaMTX path's configuration,
    with support for:
      - Safe instantiation from a dictionary (`from_dict`) with logging of unknown fields
      - Dynamic updates to existing instances (`update`) with optional strict mode
      - Serialization back to a dictionary (`to_dict`) for database or API usage

    Fields are typed and have default values matching the default configuration.

    Example Usage:
    --------------
    # --- Creating a new instance from a dict ---
    config_data = {
        "uid": "abc123",
        "source": "camera1",
        "recordEnabled": True,
        "bogusField": "ignored"
    }

    # Soft creation: unknown fields are logged, not raised
    config = MediaMTXPathConfig.from_dict(config_data)

    # Strict creation: unknown fields raise an exception
    try:
        config_strict = MediaMTXPathConfig.from_dict(config_data, strict=True)
    except AttributeError as e:
        print(e)

    # --- Updating an existing instance ---
    update_data = {
        "source": "camera2",
        "rpiCameraWidth": 1280,
        "invalidField": 123
    }

    # Soft update: logs invalidField
    config.update(update_data)

    # Strict update: raises AttributeError on invalidField
    try:
        config.update(update_data, strict=True)
    except AttributeError as e:
        print(e)

    # --- Serializing back to dict ---
    dict_repr = config.to_dict()
    print(dict_repr)
    """  
    
    uid: str = ""
    
    # mediamtx path config parameters
    source: str = "publisher"
    name: str = ""
    sourceFingerprint: str = ""
    sourceOnDemand: bool = False
    sourceOnDemandStartTimeout: str = ""
    sourceOnDemandCloseAfter: str = ""
    maxReaders: int = 0
    srtReadPassphrase: str = ""
    fallback: str = ""
    useAbsoluteTimestamp: bool = False
    record: bool = False
    recordPath: str = "/home/takusr/ots/mediamtx/recordings/%path/%Y-%m-%d%H-%M-%S-%f"
    recordFormat: str = "fmp4"
    recordPartDuration: str = "100ms"
    recordSegmentDuration: str = "1h0m0s"
    recordDeleteAfter: str = ""
    overridePublisher: bool = False
    srtPublishPassphrase: str = ""
    rtspTransport: str = "automatic"
    rtspAnyPort: bool = False
    rtspRangeType: str = ""
    rtspRangeStart: str = ""
    sourceRedirect: str = ""
    rpiCameraCamId: int = 0
    rpiCameraSecondary: bool = False
    rpiCameraWidth: int = 1024
    rpiCameraHeight: int = 768
    rpiCameraHFlip: bool = False
    rpiCameraVFlip: bool = False
    rpiCameraBrightness: int = 0
    rpiCameraContrast: int = 0
    rpiCameraSaturation: int = 0
    rpiCameraSharpness: int = 0
    rpiCameraExposure: str = "normal"
    rpiCameraAwb: str = "auto"
    #rpiCameraAwbGains: list[float] = [0.0, 0.0]    # TODO need to fix this to the proper type (keeps failing on a Go struct string64 error)
    rpiCameraDenoise: str = "off"
    rpiCameraShutter: int = 0
    rpiCameraMetering: str = "centre"
    rpiCameraGain: int = 0
    rpiCameraEv: int = 0
    rpiCameraRoi: str = ""
    rpiCameraHdr: bool = False
    rpiCameraTuningFile: str = ""
    rpiCameraMode: str = ""
    rpiCameraFps: int = 30
    rpiCameraAfMode: str = "continuous"
    rpiCameraAfRange: str = "normal"
    rpiCameraAfSpeed: str = "normal"
    rpiCameraLensPosition: int = 0
    rpiCameraAfWindow: str = ""
    rpiCameraFlickerPeriod: int = 0
    rpiCameraTextOverlayEnable: bool = False
    rpiCameraTextOverlay: str = ""
    rpiCameraCodec: str = "auto"
    rpiCameraIdrPeriod: int = 0
    rpiCameraBitrate: int = 0
    rpiCameraProfile: str = "main"
    rpiCameraLevel: str = "4.1"
    rpiCameraJpegQuality: int = 60
    runOnInit: str = ""
    runOnInitRestart: bool = False
    runOnDemand: str = ""
    runOnDemandRestart: bool = False
    runOnDemandStartTimeout: str = "10s"
    runOnDemandCloseAfter: str = "10s"
    runOnUnDemand: str = ""
    runOnReady: str = ""
    runOnReadyRestart: bool = False
    runOnNotReady: str = ""
    runOnRead: str = ""
    runOnReadRestart: bool = False
    runOnUnread: str = ""
    runOnRecordSegmentCreate: str = ""
    runOnRecordSegmentComplete: str = ""

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
                logger.warning(f"[MediaMTXPathConfig] Ignored invalid field: '{k}' (value={v!r})")

        if strict and invalid:
            raise AttributeError(f"Invalid fields for {cls.__name__}: {', '.join(invalid)}")

        return filtered
    
    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]] = None, strict: bool = False) -> "MediaMTXPathConfig":
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

    def to_complete_dict(self) -> Dict[str, Any]: return asdict(self)

    def to_mediamtx_dict(self) -> Dict[str, Any]:
        """
        Serialize to a dict suitable for MediaMTX configuration.
        Excludes: uid, name
        """
        exclude = {"uid", "name"}
        full = asdict(self)
        return {k: v for k, v in full.items() if k not in exclude}
