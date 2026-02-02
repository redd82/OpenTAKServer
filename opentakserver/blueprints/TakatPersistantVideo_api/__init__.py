# Make sure that in app.py the correct sequence of blueprints is loaded
# on line 198 this should be done first before any other blue print is registered:
#     # Register TakatApiExtensions FIRST to override endpoints from both marti_api and ots_api
#    from opentakserver.blueprints.TakatApiExtensions_api import takat_api_extensions
#    app.register_blueprint(takat_api_extensions)
#
from flask import Blueprint
from opentakserver.extensions import logger
from opentakserver.blueprints.TakatPersistantVideo_api.api import persistant_video_api
from opentakserver.blueprints.TakatPersistantVideo_api.Startup_Tasks import schedule_force_key_update

logger.info("Loading TakAT persistant video api extensions...")

# Create the main TakatApiExtensions blueprint
takat_persistant_video_api_extensions = Blueprint("takat_persistant_video_api_extensions", __name__)
# Register all sub-blueprints
takat_persistant_video_api_extensions.register_blueprint(persistant_video_api)

@takat_persistant_video_api_extensions.record_once
def _force_key_update_on_startup(state):
	schedule_force_key_update(delay_seconds=30)
