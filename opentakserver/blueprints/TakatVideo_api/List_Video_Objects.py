from opentakserver.blueprints.TakatVideo_api.Video_Object import Video_Object

# Global video object registry
VIDEO_OBJECTS = []

def add_video_object(obj: Video_Object) -> bool:
    """
    Adds a Video_Object to the global list if Camera_UID doesn't already exist.
    Returns True if added, False if a duplicate was found.
    """
    if get_video_object_by_uid(obj.UID) is None:
        VIDEO_OBJECTS.append(obj)
        return True
    return False


def remove_video_object_by_uid(camera_uid: str) -> bool:
    """
    Removes the Video_Object with the given Camera_UID.
    Returns True if removed, False if not found.
    """
    global VIDEO_OBJECTS
    original_len = len(VIDEO_OBJECTS)
    VIDEO_OBJECTS = [v for v in VIDEO_OBJECTS if v.Camera_UID != camera_uid]
    return len(VIDEO_OBJECTS) < original_len


def get_video_object_by_uid(uid: str) -> Video_Object | None:
    """
    Retrieves a Video_Object by either Camera_UID or Linked_UID.
    """
    for obj in VIDEO_OBJECTS:
        if obj.Camera_UID == uid or obj.Linked_UID == uid:
            return obj
    return None

def get_video_object_by_uid_and_otp(uid: str, otp: str) -> Video_Object | None:
    """
    Retrieves a Video_Object from the global list that allows access
    with the provided UID and OTP using the object's access_allowed method.
    """
    for obj in VIDEO_OBJECTS:
        if obj.access_allowed(uid, otp):
            return obj
    return None

def video_objects_to_dict() -> list[dict]:
    """
    Return a list of dicts representing all Video_Objects in the global VIDEO_OBJECTS list.
    """
    return [obj.to_dict() for obj in VIDEO_OBJECTS]