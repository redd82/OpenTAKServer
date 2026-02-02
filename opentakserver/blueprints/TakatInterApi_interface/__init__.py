# Make sure that in app.py the correct sequence of blueprints is loaded
# on line 198 this should be done first before any other blue print is registered:
#     # Register TakatApiExtensions FIRST to override endpoints from both marti_api and ots_api
#    from opentakserver.blueprints.TakatApiExtensions_api import takat_api_extensions
#    app.register_blueprint(takat_api_extensions)
#
from flask import Blueprint

from opentakserver.extensions import logger
from opentakserver.blueprints.TakatInterApi_interface.api import takat_inter_api

logger.info("Loading TakAT inter-API interface ...")

# Wrapper blueprint to group sub-blueprints (mirrors TakatApiExtensions pattern)
takat_inter_api_interface = Blueprint("takat_inter_api_interface", __name__)

takat_inter_api_interface.register_blueprint(takat_inter_api)
