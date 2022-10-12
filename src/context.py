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

class ContextCheck:
    """Checking context api for recent data."""

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
            LOGGER.error("  HTTP error occurred: %s", http_e)
        except Exception as e:
            LOGGER.error("  Other error occurred: %s", e)

    def check_last_ts(self, rJSON: dict) -> bool:
        # extracting data string
        locators = self.section["dateExtraction"]["path"]
        tempDateValue = rJSON

        for locator in locators:
            tempDateValue = tempDateValue[locator]

        LOGGER.info(tempDateValue)

        try:
            # extracting last timestamp from data
            datetime_pattern = re.compile(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})')
            datetime_string = datetime_pattern.search(tempDateValue).group()
            dt = datetime.strptime(datetime_string, '%Y-%m-%dT%H:%M:%S')
            # extracting difference from now
            ts = datetime.timestamp(dt)
            nowts = datetime.timestamp(datetime.now())
            diff_hrs = (nowts - ts) / 60 / 60

            if (self.section["subtype"] == "watering"):
                # implement checks for watering - carouge
                soilMoisture = rJSON["soilMoisture"]["value"]
                nextWateringDeadline = ts
                lastWateringDate = rJSON["dateLastWatering"]["value"]
                datetime_string = datetime_pattern.search(lastWateringDate).group()
                last_dt = datetime.strptime(datetime_string, '%Y-%m-%dT%H:%M:%S')

                if soilMoisture > 24:
                    pass
                # soil is dry but no watering recommendation
                elif (soilMoisture < 24) and (nextWateringDeadline < datetime.timestamp(datetime.date.today())):
                    LOGGER.error("  Low soil moisture but no new watering deadline")
                # sometimes soil is watered inbetween deadlines and could cause confusion
                elif (soilMoisture < 24) and (nextWateringDeadline < datetime.timestamp(last_dt.date())):
                    LOGGER.warning("  Soil has been watered despite no prediction.")
                else:
                    LOGGER.info("  Timestamp in the limits: %.2fh", diff_hrs)

            else:
                # check timestamp of now
                if diff_hrs > self.check["error_diff"]:
                    LOGGER.error("  Timestamp bigger than limit: %.2fh", diff_hrs)
                elif diff_hrs > self.check["alert_diff"]:
                    LOGGER.warning("  Timestamp bigger than limit: %.2fh", diff_hrs)
                else:
                    LOGGER.info("  Timestamp in the limits: %.2fh", diff_hrs)
        except Exception as e:
            LOGGER.error("  Time checking error: %s", e)