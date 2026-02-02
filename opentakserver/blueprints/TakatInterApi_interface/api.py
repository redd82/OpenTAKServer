import bleach

from OpenSSL import crypto
from OpenSSL.crypto import X509StoreFlags

from flask import current_app as app, request, Blueprint, jsonify, abort
from flask import g
from flask_security import roles_required
from flask_security.decorators import auth_required
from flask_login import current_user

from opentakserver.extensions import logger, db
from opentakserver.blueprints.TakatPersistantVideo_api.Tascomm_DB_api import Tasscom_DB_api as Dbase
from opentakserver.blueprints.TakatPersistantVideo_api.Validation import Validation
from opentakserver.blueprints.TakatInterApi_interface.jwt_auth import require_scope, verify_token
from opentakserver.blueprints.TakatInterApi_interface.defaultPluginConfig import DefaultPluginConfig as pluginConfig

takat_inter_api = Blueprint('takat_inter_api', __name__)

# Set the public JWT token for persistant video API access to Tasscomm DB API
@takat_inter_api.route("/api/TascommDB/SetJWT", methods=["POST"]) 
@require_scope("ots:server:mediamtx:token")
def set_tascommDB_jwt():
    logger.info(f"/api/TascommDB/SetJWT: {request}")
    data = request.get_json(silent=True) or {}
    token = data.get("jwt") or data.get("Jwt") or data.get("token")
    if token is None:
        return jsonify({"error": "Missing required field: jwt"}), 400

    if isinstance(token, bytes):
        token = token.decode("utf-8", errors="ignore")

    logger.info(f"TascommDB SetJWT received token: {token}")
    pluginConfig.TascommAccessToken = token

    return jsonify({"success": True,"jwt": pluginConfig.TascommAccessToken, "jwks_url": pluginConfig.JWT_JWKS_URL}), 200

@takat_inter_api.route("/api/TascommDB/GetPluginConfig", methods=["GET"])
@roles_required("administrator")
#@require_scope("ots:server:mediamtx:token")
def get_plugin_config():
    logger.info(f"TascommDB plugin Config: {pluginConfig.TascommAccessToken} {pluginConfig.TasscommFQDN} {pluginConfig.TasscommPort}")
    return jsonify({"success": True,"jwt": pluginConfig.TascommAccessToken, "fqdn": pluginConfig.TasscommFQDN, "port": pluginConfig.TasscommPort}), 200

# Set the public FQDN for persistant video API access to Tasscomm DB API
@takat_inter_api.route("/api/TascommDB/SetFQDN", methods=["POST"])  
@roles_required("administrator")
def set_tascommDB_FQDN():
    data = request.get_json(silent=True) or {}
    fqdn = data.get("fqdn") or data.get("FQDN")
    if not fqdn:
        return jsonify({"error": "Missing required field: fqdn"}), 400

    validator = Validation()
    sanitized_fqdn = validator.FQDN(fqdn)

    pluginConfig.TasscommFQDN = sanitized_fqdn

    return jsonify({"TasscommFQDN": sanitized_fqdn}), 200

# Set the public FQDN for persistant video API access to Tasscomm DB API
@takat_inter_api.route("/api/TascommDB/SetPort", methods=["POST"])  
@roles_required("administrator")
def set_tascommDB_Port():
    data = request.get_json(silent=True) or {}
    port = data.get("port") or data.get("PORT")
    if not port:
        return jsonify({"error": "Missing required field: port"}), 400

    pluginConfig.TasscommPort = port

    return jsonify({"TasscommPort": port}), 200

# @takat_inter_api.route("/api/TascommDB/Test", methods=["POST"])  
# #@require_scope("ots:server:mediamtx:token")
# def set_tascommDB_test():
#     data = request.get_json(silent=True) or {}
#     token = data.get("jwt") or data.get("Jwt") or data.get("token")
#     if not token:
#         return jsonify({"error": "Missing required field: jwt"}), 400

#     if isinstance(token, bytes):
#         token = token.decode("utf-8", errors="ignore")

#     sanitized_token = bleach.clean(token)
#     logger.info(f"TascommDB SetJWT received token: {sanitized_token}")
#     # Persist the new token and refresh the shared client
#     #plugin_config.TascommAccessToken = sanitized_token

#     return jsonify({"TascommAccessToken": sanitized_token}), 200