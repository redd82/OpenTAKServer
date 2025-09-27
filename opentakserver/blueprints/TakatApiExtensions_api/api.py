import bleach
from flask import current_app as app, request, Blueprint, jsonify
from flask_security.decorators import auth_required

from opentakserver.blueprints.ots_api.api import search, paginate
from opentakserver.extensions import logger, db
from opentakserver.models.EUD import EUD
from opentakserver.models.user import User

api_blueprint = Blueprint('takat_api_blueprint', __name__)


# TAKAT additional endpoints
@api_blueprint.route('/api/usereuds', methods=['POST'])
@auth_required()
def get_usereuds():
    # Handle case where request.json might be None
    username = None
    if request.json and 'username' in request.json:
        username = bleach.clean(request.json.get('username'))
    
    query = db.session.query(EUD)

    if username:
        query = query.join(User, User.id == EUD.user_id)
        query = query.filter(User.username == username)
    
    query = search(query, EUD, 'callsign')
    query = search(query, EUD, 'uid')
    query = search(query, User, 'username')
    return paginate(query)