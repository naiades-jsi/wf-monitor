# imports
import logging
import json
from datetime import datetime

# project imports
from src.influx_query_data import QueryFromDB

# logging
LOGGER = logging.getLogger(__name__)

class InfluxCheck:
    """Checking InfluxDB for recent data."""

    def __init__(self, section, check) -> None:
        self.section = section
        self.check = check

        # make connection to the DB
        self.queryEngine = QueryFromDB(
            self.section["token"],
            self.section["url"],
            self.section["organisation"],
            self.section["bucket"]
        )

    def run(self) -> None:
        LOGGER.info("  Building query")
        q = self.queryEngine.bucket_query()
        q = self.queryEngine.time_query(q, '-1w', '-0h')
        q = self.queryEngine.filter_query(q, self.check["measurement"])
        q = self.queryEngine.filter_last(q)
        LOGGER.info("  Running query: %s", q)
        result = self.queryEngine.query(q)

        # parse influx table
        results = []
        for table in result:
            for record in table.records:
                results.append([record.get_time(), record.get_value()])

        if results != []:
            ts = results[0][0]
            self.check_last_ts(ts)
        else:
            LOGGER.error("  No data in last week: %s", self.check["name"])

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


