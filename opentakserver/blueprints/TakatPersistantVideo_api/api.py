from flask import current_app as app, request, Blueprint, jsonify
from flask_security import roles_required

from blueprints.TakatPersistantVideo_api.DB_API import DB_API as Dbase

api_blueprint = Blueprint('takat_persistant_video_api_blueprint', __name__)

# TAKAT persistant video endpoints
@api_blueprint.route("/api/persistantvideo/test", methods=["GET"])
@roles_required("administrator")
def test_service():
    
    # create a Database interface
    DB = Dbase(mediaMTXToken="1234", fqdn="127.0.0.1", port= 8081, protocol="http", retries=3, verified_ssl=False)
    
    
    return {"success": True, "": ""}, 202


