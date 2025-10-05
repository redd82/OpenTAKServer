import logging
from typing import Optional

logger = logging.getLogger(__name__)

# assume Video_Object_v3 is imported in this module scope
from opentakserver.blueprints.TakatVideo_api.Video_Object import Video_Object_v3

VIDEO_OBJECTS: list['Video_Object_v3'] = []              # holds Video_Object_v3 instances
VIDEO_OBJECTS_MITM: list[tuple[str, str]] = []         # tuples (linked_device_uid, virtual_camera_path)


# ───────────────────────────────────────────────
# Internal helpers
# ───────────────────────────────────────────────
def _find_index_by_primary_uid(primary_uid: str) -> Optional[int]:
    """Return index of video object with given primary_uid or None if not found."""
    for i, obj in enumerate(VIDEO_OBJECTS):
        if getattr(obj, "_primary_uid", None) == primary_uid:
            return i
    return None

# ───────────────────────────────────────────────
# Public Video Objects: add / remove / update (change)
# ───────────────────────────────────────────────
def Add_Video_Object(obj: "Video_Object_v3") -> None:
    """Add a Video_Object_v3 to the global list if not already present."""
    if obj not in VIDEO_OBJECTS:
        VIDEO_OBJECTS.append(obj)
        # Also add the tuple for quick MITM reference
        Add_Tuple(obj.LinkedDevice, obj.CameraPath)

def Remove_Video_Object(obj_or_primary_uid) -> None:
    """
    Remove a Video_Object_v3 from the registry.
    Accepts either the object instance or its primary_uid string.
    Safe no-op if not present.
    """
    # resolve to instance
    if isinstance(obj_or_primary_uid, Video_Object_v3):
        obj = obj_or_primary_uid
    else:
        idx = _find_index_by_primary_uid(obj_or_primary_uid)
        obj = VIDEO_OBJECTS[idx] if idx is not None else None

    if obj is None:
        logger.debug("Remove_Video_Object: object not found, nothing to remove")
        return

    # remove MITM tuple if present
    try:
        uid, path = obj.LinkedDevice_CameraPath
        Remove_Tuple(uid, path)
    except Exception:
        logger.debug("Remove_Video_Object: could not remove MITM tuple (property missing or invalid)")

    # remove from list
    try:
        VIDEO_OBJECTS.remove(obj)
        logger.info(f"Removed Video_Object_v3 {getattr(obj, '_primary_uid', '?')} from VIDEO_OBJECTS")
    except ValueError:
        logger.debug("Remove_Video_Object: object already removed")

def Update_Video_Object(new_obj: Video_Object_v3) -> None:
    """
    Replace an existing Video_Object_v3 in VIDEO_OBJECTS with the provided instance,
    matching by primary_uid. Also update the MITM tuple (remove old, add new).
    Raises ValueError if no existing object with that primary_uid is found.
    """
    if not isinstance(new_obj, Video_Object_v3):
        raise TypeError("Update_Video_Object expects a Video_Object_v3 instance")

    primary_uid = getattr(new_obj, "_primary_uid", None)
    if not primary_uid:
        raise ValueError("Update_Video_Object: new_obj has no _primary_uid")

    idx = _find_index_by_primary_uid(primary_uid)
    if idx is None:
        raise ValueError(f"Update_Video_Object: no Video_Object_v3 found with primary_uid '{primary_uid}'")

    old_obj = VIDEO_OBJECTS[idx]

    # remove old MITM tuple (if present)
    try:
        old_uid, old_path = old_obj.LinkedDevice_CameraPath
        Remove_Tuple(old_uid, old_path)
    except Exception:
        logger.debug("Update_Video_Object: could not remove old MITM tuple")

    # replace object in list
    VIDEO_OBJECTS[idx] = new_obj
    logger.info(f"Updated Video_Object_v3 {primary_uid} in VIDEO_OBJECTS")

    # add new MITM tuple (if any)
    try:
        new_uid, new_path = new_obj.LinkedDevice_CameraPath
        Add_Tuple(new_uid, new_path)
    except Exception:
        logger.debug("Update_Video_Object: could not add new MITM tuple")

def Is_UID_Used(uid: str) -> bool:
    """
    Check if a given UID is already present in any Video_Object_v3's Used_UIDs.
    Returns True if UID exists, False otherwise.
    """
    for obj in VIDEO_OBJECTS:
        try:
            if uid in getattr(obj, "Used_UIDs", []):
                return True
        except Exception:
            continue  # defensive: skip any object that doesn’t have Used_UIDs
    return False

# ───────────────────────────────────────────────
# Tuple helpers for VIDEO_OBJECTS_MITM
# ───────────────────────────────────────────────

def Add_Tuple(uid: str, path: str) -> None:
    """Add a (uid, path) tuple if not already in VIDEO_OBJECTS_MITM."""
    tup = (uid, path)
    if tup not in VIDEO_OBJECTS_MITM:
        VIDEO_OBJECTS_MITM.append(tup)

def Remove_Tuple(uid: str, path: str) -> None:
    """Remove a (uid, path) tuple if present in VIDEO_OBJECTS_MITM."""
    tup = (uid, path)
    if tup in VIDEO_OBJECTS_MITM:
        VIDEO_OBJECTS_MITM.remove(tup)

def Find_Path_By_UID(uid: str) -> str | None:
    """
    Check if a UID exists in VIDEO_OBJECTS_MITM.
    If found, return the associated path string.
    If not found, return None.
    """
    for linked_uid, path in VIDEO_OBJECTS_MITM:
        if linked_uid == uid:
            return path
    return None

