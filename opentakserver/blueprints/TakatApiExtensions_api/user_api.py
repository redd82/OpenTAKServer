
import bleach
from flask import current_app as app, request, Blueprint, jsonify
from flask_login import current_user
from flask_security.decorators import roles_accepted, auth_required

from opentakserver.blueprints.ots_api.api import search, paginate
from opentakserver.extensions import logger, db
from opentakserver.models.user import User

user_api_blueprint = Blueprint('takat_user_api_blueprint', __name__)


# TAKAT Additional API call for filtering single user
@user_api_blueprint.route('/api/user/get', methods=['POST'])
@roles_accepted('administrator')
def get_user_data():
    if not request.json or 'username' not in request.json:
        return jsonify({"success": False, "error": "Username is required"}), 400
    
    username = bleach.clean(request.json.get('username'))
    if not username:
        return jsonify({"success": False, "error": "Invalid username"}), 400
        
    query = db.session.query(User)
    query = query.filter(User.username == username)
    query = search(query, User, 'username')
    return paginate(query)

# TAKAT Additional API call for filtering own user
@user_api_blueprint.route('/api/user/getOwnuser')
@auth_required()
def get_ownuser_data():
    user = current_user
    query = db.session.query(User)
    query = query.filter(User.username == user.username)
    query = search(query, User, 'username')
    return paginate(query)

