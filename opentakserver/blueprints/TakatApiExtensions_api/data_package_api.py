import os
from flask import Blueprint, request, current_app as app, send_from_directory
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
    return paginate(query)

# TAKAT API route overload for own implementation
# removed auth required so users can download package. Chance of package hash being guessed is small.
# @data_package_api.route('/api/data_packages/download')
# def data_package_download():
#     if 'hash' not in request.args.keys():
#         return ({'success': False, 'error': 'Please provide a data package hash'}, 400,
#                 {'Content-Type': 'application/json'})

#     file_hash = request.args.get('hash')

#     query = db.session.query(DataPackage)
#     query = search(query, DataPackage, 'hash')

#     data_package = db.session.execute(query).first()

#     if not data_package:
#         return ({'success': False, 'error': "Data package with hash '{}' not found".format(file_hash)}, 404,
#                 {'Content-Type': 'application/json'})

#     download_name = data_package[0].filename
#     name, extension = os.path.splitext(download_name)

#     return send_from_directory(app.config.get("UPLOAD_FOLDER"), f"{file_hash}{extension}", as_attachment=True,
#                                download_name=download_name)
