from flask import Blueprint
from flask_login import current_user
from flask_security.decorators import auth_required

from opentakserver.blueprints.ots_api.api import search, paginate
from opentakserver.extensions import db
from opentakserver.models.DataPackage import DataPackage
from opentakserver.models.user import User

data_package_api = Blueprint('takat_data_package_api', __name__)


# TAKAT adaptation so only the administrator can see all data packages
# and the rest can only see their own data packages
@data_package_api.route('/api/data_packages')
@auth_required()
def data_packages():
    user = current_user
    print(user.username)
    query = db.session.query(DataPackage)
    if user.username != "administrator":
        query = query.join(DataPackage.user).filter(User.username == user.username)
    # query = query.filter(DataPackage.keywords == 'private')
    # query = search(query, DataPackage, 'filename')
    # query = search(query, DataPackage, 'hash')
    # query = search(query, DataPackage, 'createor_uid')
    # query = search(query, DataPackage, 'keywords')
    # query = search(query, DataPackage, 'mime_type')
    # query = search(query, DataPackage, 'size')
    # query = search(query, DataPackage, 'tool')
    return paginate(query)