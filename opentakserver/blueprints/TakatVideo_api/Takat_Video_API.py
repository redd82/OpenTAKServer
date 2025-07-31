from flask import Blueprint, request, jsonify, Response, json

# Import the default configuration
from opentakserver.defaultconfig import DefaultConfig # <- this is how OTS loads configuration values centrally
import requests
# video object
from opentakserver.blueprints.TakatVideo_api import Video_Object as Video_Object

#util 
from opentakserver.blueprints.TakatVideo_api.util import Util_Safe_Hyperlink as Link  # safe hyperlink object
#Global List
from opentakserver.blueprints.TakatVideo_api.List_Video_Objects import VIDEO_OBJECTS, add_video_object, remove_video_object_by_uid, get_video_object_by_uid,get_video_object_by_uid_and_otp


# --- ThreadPoolExecutor configuration ---
from concurrent.futures import ThreadPoolExecutor
MAX_STREAM_THREADS = 25                                                 #hard coded limit to garantuee performance
stream_executor = ThreadPoolExecutor(max_workers=MAX_STREAM_THREADS)


# runtime setup, call via TAKAT/Setup 
# should be repeated after any/all server reboots.

# config data for the mediamtx server (where to find it and how to access it)
TAKAT_mediamtx_protocol = "http"
TAKAT_mediamtx_ip = "127.0.0.1" 
TAKAT_mediamtx_api_port = 9997 
TAKAT_mediamtx_streaming_port = 8554
TAKAT_mediamtx_token = ""
# config data for the tak server itself,
TAKAT_tak_server_protocol = "http"
TAKAT_tak_server_ip = "127.0.0.1"
TAKAT_tak_server_api_port = 8443
TAKAT_tak_server_token = ""
# config data for things to do with commecrial use
TAKAT_tak_server_Free = False  # This is a flag to indicate if the TAK server is an unpaid/free version, which may have limitations on features or performance.
TAKAT_commercial_text_overlay = "TAKAT.NL - %Y-%m-%d %H:%M:%S - TAKAT.NL"  # Default text overlay for non-commercial users

# register
video_bp = Blueprint('Takat_Video_API', __name__)

Debug = True
Setup_Lock = False  # Lock to prevent multiple setups during runtime

@video_bp.route('/Register', methods=['POST'])
def register_camera():
    # create Video_Object from request data
    # create MediamTX path
    # Create virtual camera path
    # Add to managed object list
    #if all went well, return 200 OK with path to camera stream and otp
    #mandatory
   pass
    
    
    
@video_bp.route('/Unregister', methods=['POST'])
def unregister_camera():
    pass

    
@video_bp.route('/ServerSetup', methods=['POST'])
def ServerSetup():
    """
    tak server ip/fqdn
    tak server api port
    tak server token
    mediamtx server ip/fqdn
    mediamtx server api port
    mediamtx server token    
    
    at server (re)boot setup the takat server configuration, we need ip's/fqdn's that the OTS and the mediamtx server use to call eachothers api's
    theese can be both internal ip's or fqdn's, but the OTS server needs to be able to reach the mediamtx server and vice versa.
    
    note, Self_locking allows the setup to be locked after the first setup, preventing changes during runtime but can be set to false for debugging purposes.
    """
    
    #TODO : Add authentication logic here
    # This is a simple setup endpoint to configure the TAKAT server settings.
    # It allows setting the MediaMTX and TAK server configurations, including protocol, IP,
    # API port, and token. It also supports a self-locking mechanism to prevent changes
    # during runtime after the initial setup.
    
    global TAKAT_mediamtx_protocol, TAKAT_mediamtx_ip, TAKAT_mediamtx_api_port, TAKAT_mediamtx_token, TAKAT_mediamtx_streaming_port
    global TAKAT_tak_server_protocol, TAKAT_tak_server_ip, TAKAT_tak_server_api_port, TAKAT_tak_server_token
    global TAKAT_tak_server_Free, TAKAT_commercial_text_overlay
    global Setup_Lock
    # TODO: Add authentication logic here
    
    data = request.get_json()
    self_locking = data.get('self_locking', True)  # Default to True if not provided
    
    if Setup_Lock == False:
        try:
            if data.get('commercial_text_overlay'):
                TAKAT_commercial_text_overlay = data['commercial_text_overlay']
            if data.get('free_tak_server'):
                TAKAT_tak_server_Free = data['free_tak_server']
            if data.get ('mediamtx_protocol'):
                TAKAT_mediamtx_protocol = data['mediamtx_protocol']
            if data.get('mediamtx_ip'):
                TAKAT_mediamtx_ip = data['mediamtx_ip']
            if data.get('mediamtx_api_port'):
                TAKAT_mediamtx_api_port = data['mediamtx_api_port']
            if data.get('TAKAT_mediamtx_streaming_port'):
                TAKAT_mediamtx_streaming_port = data['mediamtx_streaming_port']
            if data.get('mediamtx_token'):
                TAKAT_mediamtx_token = data['mediamtx_token']
            if data.get('tak_server_protocol'):
                TAKAT_tak_server_protocol = data['tak_server_protocol']
            if data.get('tak_server_ip'):
                TAKAT_tak_server_ip = data['tak_server_ip']
            if data.get('tak_server_api_port'):
                TAKAT_tak_server_api_port = data['tak_server_api_port']
            if data.get('tak_server_token'):
                TAKAT_tak_server_token = data['tak_server_token']

            if self_locking == True:   # Lock the setup automatically after the first setup
                Setup_Lock = True  # Lock the setup to prevent changes during runtime
            
            return jsonify({
                "message": "TAKAT configuration is now:",
                "mediamtx_protocol": TAKAT_mediamtx_protocol,
                "mediamtx_ip": TAKAT_mediamtx_ip,
                "mediamtx_api_port": TAKAT_mediamtx_api_port,
                "mediamtx_streaming_port": TAKAT_mediamtx_streaming_port,
                "mediamtx_token": "SuperSecret",
                "tak_server_protocol": TAKAT_tak_server_protocol,
                "tak_server_ip": TAKAT_tak_server_ip,
                "tak_server_api_port": TAKAT_tak_server_api_port,
                "tak_server_token": "SuperSecret",
                "tak_server_free_version": TAKAT_tak_server_Free,
                "tak_server_commercial_text_overlay": TAKAT_commercial_text_overlay,
                "self_locking": self_locking,
                "Setup_Lock": Setup_Lock
            }), 200
            
        except Exception as e:
            return jsonify({
                "error": "Setup failed",
                "details": str(e),
                "Setup_Lock": Setup_Lock
            }), 400 
    else:
        return jsonify({
            "error": "Setup Lock is on, cannot change configuration.",
            "mediamtx_protocol": TAKAT_mediamtx_protocol,
            "mediamtx_ip": TAKAT_mediamtx_ip,
            "mediamtx_api_port": TAKAT_mediamtx_api_port,
            "mediamtx_streaming_port": TAKAT_mediamtx_streaming_port,
            "mediamtx_token": "SuperSecret",
            "tak_server_protocol": TAKAT_tak_server_protocol,
            "tak_server_ip": TAKAT_tak_server_ip,
            "tak_server_api_port": TAKAT_tak_server_api_port,
            "tak_server_token": "SuperSecret",
            "tak_server_free_version": TAKAT_tak_server_Free,
            "tak_server_commercial_text_overlay": TAKAT_commercial_text_overlay,
            "self_locking": self_locking,
            "Setup_Lock": Setup_Lock
        }), 403