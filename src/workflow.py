# imports
import logging
import json

# project imports
from src.historic import HistoricCheck
from src.influx import InfluxCheck
from src.kafka import KafkaCheck

# logging
LOGGER = logging.getLogger(__name__)

class Workflow:
    """Managing a particular workflow for NAIADES project."""

    def __init__(self, workflow: str = "carouge") -> None:
        config_directory = "configs"

        # differentiate between different workflows
        if (workflow == "carouge"):
            self.config_file = f"{config_directory}/carouge.json"
        elif (workflow == "alicante-consumption"):
            self.config_file = f"{config_directory}/alicante-consumption.json"
        elif (workflow == "alicante-salinity"):
            self.config_file = f"{config_directory}/salinity.json"
        elif (workflow == "braila-consumption"):
            self.config_file = f"{config_directory}/braila-consumption.json"
        elif (workflow == "braila-anomaly"):
            self.config_file = f"{config_directory}/braila-anomaly.json"
        else:
            LOGGER.error("No config was recognised: %s", workflow)

        LOGGER.info("Loading config: %s", self.config_file)
        with open(self.config_file, "r") as json_file:
            self.config = json.load(json_file)

    def check(self) -> None:
        LOGGER.info("Starting worklfow check")

        for section in self.config["workflow"]:
            LOGGER.info("Starting checks for: %s", section["name"])

            for check in section["checks"]:
                self.check_item(section, check)

    def check_item(self, section: dict, check: dict) -> None:
        LOGGER.info("Checking: %s", check["name"])
        if (section["type"] == "naiades_historic"):
            myCheck = HistoricCheck(section, check)
            myCheck.run()
        if (section["type"] == "influx"):
            myCheck = InfluxCheck(section, check)
            myCheck.run()
        if (section["type"] == "kafka"):
            myCheck = KafkaCheck(section, check)
            myCheck.run()

"""
  measurements_analog = [
    #'flow211106H360',
    'flow211206H360',
    'flow211306H360',
    'flow318505H498'
    ]
measurements_presure = [
    'pressure5770',
    'pressure5771',
    'pressure5772',
    'pressure5773'
    ]
"""