from flask import Blueprint

from opentakserver.blueprints.TakatVideo_api.util_api import TakatVideo
from opentakserver.blueprints.TakatVideo_api.Takat_Video_API import video_bp

TakatVideo_blueprint = Blueprint("takatvideo_blueprint", __name__)

TakatVideo_blueprint.register_blueprint(TakatVideo)
TakatVideo_blueprint.register_blueprint(video_bp)
