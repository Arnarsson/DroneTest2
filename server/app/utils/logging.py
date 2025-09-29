import logging
import sys
import os

def configure_logging():
    level = logging.DEBUG if os.getenv("ENV","dev")=="dev" else logging.INFO
    fmt = "[%(asctime)s] %(levelname)s %(name)s :: %(message)s"
    logging.basicConfig(stream=sys.stdout, level=level, format=fmt)
    for noisy in ("uvicorn.access","asyncio","sqlalchemy.engine.Engine"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
    return logging.getLogger("dronewatch")