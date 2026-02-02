from flask import current_app as app, request, Blueprint, jsonify
from flask_security import roles_required
from flask_security.decorators import auth_required
from flask_login import current_user



from flask import request, jsonify
from typing import Optional

from opentakserver.blueprints.TakatPersistantVideo_api.Tascomm_DB_api import Tasscom_DB_api as Dbase
from opentakserver.blueprints.TakatPersistantVideo_api.MediaMTX_api import MediaMTX_api 
from opentakserver.blueprints.TakatPersistantVideo_api.models.MediaMTXPathConfig import MediaMTXPathConfig as MediaMTXConfig
from opentakserver.blueprints.TakatPersistantVideo_api.Validation import Validation
from opentakserver.blueprints.TakatInterApi_interface.defaultPluginConfig import DefaultPluginConfig as pluginConfig

# Blueprint for persistant video API
persistant_video_api = Blueprint("persistant_video_api", __name__)

#public mediamtx interface
Public_MediaMTX_Interface = MediaMTX_api(fqdn="127.0.0.1", port=9997, retries=3, verified_ssl=False)   # public interface (temporary)
# public tasscomm db interface
Public_TascommDB_Interface = Dbase(retries=3, log=True, debug=True)   # public interface (temporary) 


# --------------------------------------------------------------------------------------
# TAKAT persistant video endpoints interact with mediamtx server(s)
# --------------------------------------------------------------------------------------

@persistant_video_api.route("/api/persistantvideo/MediaMTX/AddPath", methods=["POST"])
@roles_required("administrator")
def MediaMTX_AddPath():
    data = request.get_json(silent=True) or {}

    # Required field
    uid = data.get("uid")
    if not uid:
        return jsonify({"error": "Missing required field: uid"}), 400

    # Optional fields with defaults
    fqdn: Optional[str] = data.get("fqdn") or "127.0.0.1"   # default to localhost if not provided 
    port: int = data.get("port") or 9997    # default port 9997
    retries: int = data.get("retries") or 0 # default retries to 0   
    
    verified_ssl = bool(data.get("verified_ssl")) if data.get("verified_ssl") is not None else False #get the verified_ssl flag if provided, else default to False  
  
    Jwt: Optional[str] = data.get("Jwt")    #default to empty string if not provided
    
    log: bool = bool(data.get("log")) if data.get("log") is not None else False #get the log flag if provided, else default to False

    # Config is nested object, also optional
    config = MediaMTXConfig()  # default config
    
    #payload = all other json data not specifically parsed above
    excluded = {"uid", "fqdn", "port", "retries", "verified_ssl", "Jwt", "log", "name"} #fields to exclude from config update
    payload = {k: v for k, v in data.items() if k not in excluded} # get the remaining fields for config update
     
    config.update(payload) # update config with remaining fields
    
    # ---- Perform your actual logic here ----
    return jsonify({"Added": Public_MediaMTX_Interface.CreatePath(uid=uid, fqdn=fqdn, port=port, retries=retries, 
                                                                  verified_ssl=verified_ssl, Jwt=Jwt, log=log, 
                                                                  config=config.to_mediamtx_dict())}), 200 
    

@persistant_video_api.route("/api/persistantvideo/MediaMTX/DeletePath", methods=["POST"])
@roles_required("administrator")
def MediaMTX_DeletePath():
    data = request.get_json(silent=True) or {}

    # Required field
    uid = data.get("uid")
    if not uid:
        return jsonify({"error": "Missing required field: uid"}), 400

    # Optional fields with defaults
    fqdn: Optional[str] = data.get("fqdn")
    port: int = data.get("port") or 9997
    retries: int = data.get("retries") or 0
    
    verified_ssl = bool(data.get("verified_ssl")) if data.get("verified_ssl") is not None else False
  
    Jwt: Optional[str] = data.get("Jwt") if data.get("Jwt") is not None else ""
    log: bool = bool(data.get("log")) if data.get("log") is not None else False
    
    # ---- Perform your actual logic here ----
    return jsonify({"Deleted": Public_MediaMTX_Interface.DeletePath(uid=uid, fqdn=fqdn, port=port, retries=retries, verified_ssl=verified_ssl, Jwt=Jwt, log=log)}), 200 
                                                                
@persistant_video_api.route("/api/persistantvideo/MediaMTX/GetPath", methods=["POST"])
@roles_required("administrator")
def MediaMTX_GetPath(): 
    data = request.get_json(silent=True) or {}

    # Required field
    uid = data.get("uid")
    if not uid:
        return jsonify({"error": "Missing required field: uid"}), 400

    # Optional fields with defaults
    fqdn: Optional[str] = data.get("fqdn")
    port: int = data.get("port") or 9997
    retries: int = data.get("retries") or 0
    
    verified_ssl = bool(data.get("verified_ssl")) if data.get("verified_ssl") is not None else False
  
    Jwt: Optional[str] = data.get("Jwt") if data.get("Jwt") is not None else ""
    log: bool = bool(data.get("log")) if data.get("log") is not None else False
    
    # ---- Perform your actual logic here ----
    return jsonify({"Configuration": Public_MediaMTX_Interface.GetPath(uid=uid, fqdn=fqdn, port=port, retries=retries, verified_ssl=verified_ssl, Jwt=Jwt, log=log)}), 200 
 
@persistant_video_api.route("/api/persistantvideo/MediaMTX/GetAllPaths", methods=["GET"])
@roles_required("administrator")
def MediaMTX_GetAllPaths():
    """
        Retrieve the list of MediaMTX paths using optional REST override parameters.

        This endpoint accepts an optional JSON body containing temporary override
        values for FQDN, port, retry count, SSL verification, JWT authentication,
        and logging. If fields are omitted, sensible defaults are applied.  
        The function calls `Public_MediaMTX_Interface.ListPaths()` with the parsed
        values and returns the resulting configuration in JSON format.

        Request JSON Body (optional):
            fqdn (str, optional):
                Override the target hostname or IP for the MediaMTX REST API.
            port (int, optional):
                Override the REST API port. Defaults to 9997.
            retries (int, optional):
                Number of retry attempts for the REST call. Defaults to 0.
            verified_ssl (bool, optional):
                Whether SSL certificate verification should be enabled. Defaults to False.
            Jwt (str, optional):
                JWT token for authenticated MediaMTX endpoints. Defaults to empty string.
            log (bool, optional):
                Whether to enable verbose logging during the REST call. Defaults to False.

        Returns:
            tuple:
                A Flask JSON response in the format:
                {
                    "Configuration": <result of ListPaths(...)>
                }
                along with HTTP status code 200.
    """
    
    data = request.get_json(silent=True) or {}

    # Optional fields with defaults
    fqdn: Optional[str] = data.get("fqdn")
    port: int = data.get("port") or 9997
    retries: int = data.get("retries") or 0
    
    verified_ssl = bool(data.get("verified_ssl")) if data.get("verified_ssl") is not None else False
  
    Jwt: Optional[str] = data.get("Jwt") if data.get("Jwt") is not None else ""
    log: bool = bool(data.get("log")) if data.get("log") is not None else False
    
    # ---- Perform your actual logic here ----
    return jsonify({"Configuration": Public_MediaMTX_Interface.ListPaths(fqdn=fqdn, port=port, retries=retries, verified_ssl=verified_ssl, Jwt=Jwt, log=log)}), 200 
 
@persistant_video_api.route("/api/persistantvideo/MediaMTX/PatchPath", methods=["PATCH"])
@roles_required("administrator")
def MediaMTX_PatchPath():
    data = request.get_json(silent=True) or {}

    # Required field
    uid = data.get("uid")
    if not uid:
        return jsonify({"error": "Missing required field: uid"}), 400

    # Optional fields with defaults
    fqdn: Optional[str] = data.get("fqdn")
    port: int = data.get("port") or 9997
    retries: int = data.get("retries") or 0
    
    verified_ssl = bool(data.get("verified_ssl")) if data.get("verified_ssl") is not None else False
  
    Jwt: Optional[str] = data.get("Jwt") if data.get("Jwt") is not None else ""
    log: bool = bool(data.get("log")) if data.get("log") is not None else False
    
    #payload = all other json data not specifically parsed above
    excluded = {"uid", "fqdn", "port", "retries", "verified_ssl", "Jwt", "log", "name"} #fields to exclude from config update
    
    updates = {k: v for k, v in data.items() if k not in excluded}
    loaded_config = Public_MediaMTX_Interface.GetPath(
        uid=uid,
        fqdn=fqdn,
        port=port,
        retries=retries,
        verified_ssl=verified_ssl,
        Jwt=Jwt,
        log=log,
    )
    
    if not loaded_config: return jsonify({"error": f"Path with uid {uid} not found"}), 404 # darnit, we can't get the config to patch
    
    loaded_config.update(updates) # update config with remaining fields
    
    result = Public_MediaMTX_Interface.PatchPath(
        uid=uid,
        fqdn=fqdn,
        port=port,
        retries=retries,
        verified_ssl=verified_ssl,
        Jwt=Jwt,
        updates=loaded_config,
        log=log,
    )   # patch the path
    
    return jsonify({"Updated Configuration": result}), 200

# --------------------------------------------------------------------------------------
# Tasscomm DB API JWT token management endpoints
# --------------------------------------------------------------------------------------
@persistant_video_api.route("/api/persistantvideo/TascommDB/ForceKeyUpdate", methods=["GET"])  
@roles_required("administrator")
def ForceKeyUpdate():
    output = Public_TascommDB_Interface.ForceKeyUpdate()
    return jsonify({"data": output}), 200


@persistant_video_api.route("/api/persistantvideo/TascommDB/GetAllVideoObjects", methods=["POST"])
@roles_required("administrator")
def GetAllVideoObjects_tascommDB_api():
    # Read JSON body safely
    data = request.get_json(silent=True) or {}

    # Get required field
    restoutput = data.get("restoutput")
    # Ensure it's a boolean
    if isinstance(restoutput, bool):
        restoutput_bool = restoutput
    elif isinstance(restoutput, str):
        restoutput_bool = restoutput.lower() in ("true", "1", "yes")
    elif isinstance(restoutput, int):
        restoutput_bool = restoutput != 0
    elif restoutput is None:
        return jsonify({"error": "Missing required field: restoutput"}), 400
    else:
        return jsonify({"error": "Invalid type for restoutput, must be boolean"}), 400
    
    # Call your DB API
    output = Public_TascommDB_Interface.GetAllVideoObjects(RestOutput=restoutput_bool)

    # Determine what to return
    if restoutput_bool:
        # If RestOutput=True, the API already wraps the data with body/header/etc.
        return output, 200
    else:
        # Otherwise, just return the raw list of video objects
        video_objects = output.get("videoObject", []) if isinstance(output, dict) else []
        return jsonify(video_objects), 200



# NON FUNCTIONAL BELOW HERE


@persistant_video_api.route("/api/persistantvideo/TascommDB/GetAllVideoObjectUIDs", methods=["GET"])  
#@roles_required("administrator")
def GetAllVideoObjectUIDs_tascommDB_api():
    output = Public_TascommDB_Interface.GetAllVideoObjectUIDs()
    return jsonify({"data": output}), 200

@persistant_video_api.route("/api/persistantvideo/TascommDB/DoesUIDExist", methods=["POST"])  
#@roles_required("administrator")
def DoesUIDExist():
    data = request.get_json(silent=True) or {}
    uid = data.get("uid")
    if not uid:
        return jsonify({"error": "Missing required field: uid"}), 400
    else:
        output = Public_TascommDB_Interface.DoesUIDExist(uid=uid)
    return jsonify({"data": output}), 200


@persistant_video_api.route("/api/persistantvideo/TascommDB/Test", methods=["POST"])  
#@roles_required("administrator")
def Test():

    # Read JSON body safely
    data = request.get_json(silent=True) or {}

    # Get required fields
    
    #do we a complete rest output or do we want to jsonify it ourselves
    restoutput = data.get("restoutput")
    # Ensure it's a boolean
    if isinstance(restoutput, bool):
        restoutput_bool = restoutput
    elif isinstance(restoutput, str):
        restoutput_bool = restoutput.lower() in ("true", "1", "yes")
    elif isinstance(restoutput, int):
        restoutput_bool = restoutput != 0
    elif restoutput is None:
        return jsonify({"error": "Missing required field: restoutput"}), 400
    else:
        return jsonify({"error": "Invalid type for restoutput, must be boolean"}), 400
    
     # --- Validate UID ---
    Uid = data.get("uid")
    if not isinstance(Uid, str) or not Uid.strip():
        return jsonify({"error": "Missing or invalid UID, must be a non-empty string"}), 400

    
    # Call your DB API
    output = Public_TascommDB_Interface.DoesUIDExist(uid=Uid, restoutput=restoutput_bool)
    

    # Determine what to return
    if restoutput_bool:
        # If RestOutput=True, the API already wraps the data with body/header/etc.
        return output, 200
    else:
        # Otherwise, just return the raw list of video objects
        video_objects = output.get("videoObject", []) if isinstance(output, dict) else []
        return jsonify(video_objects), 200