# Make sure that in app.py the correct sequence of blueprints is loaded
# on line 198 this should be done first before any other blue print is registered:
#     # Register TakatApiExtensions FIRST to override endpoints from both marti_api and ots_api
#    from opentakserver.blueprints.TakatApiExtensions_api import takat_api_extensions
#    app.register_blueprint(takat_api_extensions)
#
from flask import Blueprint
from opentakserver.blueprints.TakatApiExtensions_api.user_api import user_api_blueprint
from opentakserver.blueprints.TakatApiExtensions_api.api import api_blueprint
from opentakserver.blueprints.TakatApiExtensions_api.data_package_api import data_package_api
from opentakserver.blueprints.TakatApiExtensions_api.marti_api import data_package_marti_api
from opentakserver.blueprints.TakatApiExtensions_api.token_api import token_api_blueprint

# Create the main TakatApiExtensions blueprint
takat_api_extensions = Blueprint("takat_api_extensions", __name__)

# Register all sub-blueprints
takat_api_extensions.register_blueprint(user_api_blueprint)
takat_api_extensions.register_blueprint(api_blueprint)
takat_api_extensions.register_blueprint(data_package_api)
takat_api_extensions.register_blueprint(data_package_marti_api)
takat_api_extensions.register_blueprint(token_api_blueprint)
