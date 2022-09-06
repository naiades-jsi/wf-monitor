# imports
import logging
import json
import requests
from requests.exceptions import HTTPError
from datetime import datetime
import re # regular expressions

# project imports

# logging
LOGGER = logging.getLogger(__name__)

class HistoricCheck:
    """Checking historic api for recent data."""

    def __init__(self, section, check) -> None:
        self.section = section
        self.check = check

    def run(self) -> None:
        try:
            # make a requst
            url = self.section["url"].format(self.check["device"])
            response = requests.get(url, headers=self.section["headers"])
            LOGGER.info("  Trying: %s", url)
            rJSON = response.json()

            if (self.check_last_ts(rJSON) == False):
                LOGGER.error("")

        except HTTPError as http_e:
            LOGGER.error(f'  HTTP error occurred: {http_e}')
        except Exception as e:
            LOGGER.error(f'  Other error occurred: {e}')
        # this might be misleading for the user if any errors happen through checking
        # else:
        #    LOGGER.info("HTTP Request successful.")

    def check_last_ts(self, rJSON: dict) -> bool:
        try:
            # extracting last timestamp from data
            date_string = rJSON["index"][0]
            datetime_pattern = re.compile(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})')
            datetime_string = datetime_pattern.search(date_string).group()
            dt = datetime.strptime(datetime_string, '%Y-%m-%dT%H:%M:%S')
            # extracting difference from now
            ts = datetime.timestamp(dt)
            nowts = datetime.timestamp(datetime.now())
            diff_hrs = (nowts - ts) / 60 / 60

            # check timestamp of now
            if diff_hrs > self.check["error_diff"]:
                LOGGER.error("  Timestamp bigger then limit: %.2fh", diff_hrs)
            elif diff_hrs > self.check["alert_diff"]:
                LOGGER.warning("  Timestamp bigger then limit: %.2fh", diff_hrs)
            else:
                LOGGER.info("  Timestamp in the limits: %.2fh", diff_hrs)
        except Exception as e:
            LOGGER.error(f'  Time checking error: {e}')


