# imports
import logging
import json
from datetime import datetime

# project imports

# logging
LOGGER = logging.getLogger(__name__)

class KafkaCheck:
    """Checking InfluxDB for recent data."""

    def __init__(self, section, check) -> None:
        self.section = section
        self.check = check

    def run(self) -> None:
        LOGGER.info("  Queryjing topic")

    def check_last_ts(self, dt: datetime) -> bool:
        try:
            # extracting difference from now
            ts = datetime.timestamp(dt)
            nowts = datetime.timestamp(datetime.now())
            diff_hrs = (nowts - ts) / 60 / 60

            # check timestamp of now
            if diff_hrs > self.check["error_diff"]:
                LOGGER.error("  Timestamp bigger then limit: %fh", diff_hrs)
            elif diff_hrs > self.check["alert_diff"]:
                LOGGER.warning("  Timestamp bigger than limit: %fh", diff_hrs)
            else:
                LOGGER.info("  Timestamp in the limits: %fh", diff_hrs)
        except Exception as e:
            LOGGER.error(f'  Time checking error: {e}')


