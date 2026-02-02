
import traceback
import bleach
from flask import current_app as app, request, Blueprint, jsonify
from flask_login import current_user
from flask_security.decorators import roles_accepted, auth_required

from opentakserver.blueprints.ots_api.api import search, paginate
from opentakserver.extensions import logger, db
from opentakserver.models.user import User
from opentakserver.blueprints.TakatApiExtensions_api.models.TakatUser import TakatUser
from opentakserver.blueprints.TakatInterApi_interface.jwt_auth import verify_token, require_scope

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
        
    query = db.session.query(TakatUser)
    query = query.filter(TakatUser.username == username)
    query = search(query, TakatUser, 'username')
    return paginate(query)

# TAKAT Additional API call for filtering own user
@user_api_blueprint.route('/api/user/getOwnuser')
@auth_required()
def get_ownuser_data():
    user = current_user
    query = db.session.query(TakatUser)
    query = query.filter(TakatUser.username == user.username)
    query = search(query, TakatUser, 'username')
    return paginate(query)

# TAKAT API route overload for own implementation
@user_api_blueprint.route('/api/users')
#@roles_accepted('administrator')
@require_scope("ots:user:read")
def get_users():
    query = db.session.query(TakatUser)
    query = search(query, TakatUser, 'username')

    return paginate(query)

@user_api_blueprint.route("/api/user/delete", methods=['POST'])
@roles_accepted("administrator")
def delete_user():
    data = request.get_json(silent=True)
    if not data or 'username' not in data:
        return jsonify({'success': False, 'error': 'Username is required'}), 400

    username = bleach.clean(data.get('username'))
    if not username:
        return jsonify({'success': False, 'error': 'Invalid username'}), 400

    if username == current_user.username:
        return jsonify({'success': False, 'error': "You can't delete your own account"}), 400

    if username in ("administrator", "Triz"):
        return jsonify({'success': False, 'error': "You can't delete a system account"}), 400

    logger.info("Deleting user {}".format(username))

    try:
        security = app.extensions.get('security')
        if not security:
            raise RuntimeError('Flask-Security extension is not initialized')
        user = security.datastore.find_user(username=username)
        security.datastore.delete_user(user)
    except BaseException as e:
        logger.error(traceback.format_exc())
        return {'success': False, 'error': 'Failed to delete user: {}'.format(e)}, 400

    db.session.commit()
    return {'success': True}, 200, {'Content-Type': 'application/json'}