from flask import current_app as app, request, Blueprint, jsonify
from flask_security import roles_required

from blueprints.TakatPersistantVideo_api.Tascomm_DB import Tasscom_DB_API as Dbase

persistant_video_api_blueprint = Blueprint('takat_persistant_video_api_blueprint', __name__)

# TAKAT persistant video endpoints
@persistant_video_api_blueprint.route("/api/persistantvideo/test", methods=["GET"])
@roles_required("administrator")
def test_service():
    
    # create a Database interface
    # http://192.168.18.120:10301/devapi/ 
    DB = Dbase(TascommToken="auto", fqdn="192.168.18.120", port= 10301, protocol="http", retries=3, verified_ssl=False)
    
    
    return {"success": True, "": ""}, 202


