import threading

from opentakserver.extensions import logger
from opentakserver.blueprints.TakatPersistantVideo_api.Tascomm_DB_api import Tasscom_DB_api as Dbase


def schedule_force_key_update(delay_seconds: int = 30) -> None:
    def _run() -> None:
        logger.info("Running Tascomm DB ForceKeyUpdate on startup...")
        try:
            Dbase().ForceKeyUpdate()
        except Exception as exc:
            logger.error(f"ForceKeyUpdate failed during startup: {exc}")

    threading.Timer(delay_seconds, _run).start()
