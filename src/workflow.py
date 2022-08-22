# imports
import logging
import json

# project imports
from src.historic import HistoricCheck
from src.influx import InfluxCheck

# logging
LOGGER = logging.getLogger(__name__)

class Workflow:
    """Managing a particular workflow for NAIADES project."""

    def __init__(self, workflow: str = "carouge") -> None:
        config_directory = "configs"
        if (workflow == "carouge"):
            self.config_file = f"{config_directory}/carouge.json"
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
        #if (section["type"] == "naiades_historic"):
        #    myCheck = HistoricCheck(section, check)
        #    myCheck.run()
        if (section["type"] == "influx"):
            myCheck = InfluxCheck(section, check)
            myCheck.run()
