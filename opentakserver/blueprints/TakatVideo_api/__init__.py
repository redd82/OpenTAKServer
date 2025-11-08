from flask import Blueprint

from opentakserver.extensions import logger
from opentakserver.blueprints.TakatVideo_api.util_api import TakatVideo
from opentakserver.blueprints.TakatVideo_api.Takat_Video_API import video_bp

logger.info("Loading TakAT Video api extensions...")

TakatVideo_blueprint = Blueprint("takatvideo_blueprint", __name__)

TakatVideo_blueprint.register_blueprint(TakatVideo)
TakatVideo_blueprint.register_blueprint(video_bp)
