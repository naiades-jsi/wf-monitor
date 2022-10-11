# Python module imports
import argparse
import json
import sys
import time
import logging

# project imports
from src.workflow import Workflow

# logging
LOGGER = logging.getLogger("wf-monitor")
logging.basicConfig(
    format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s", level=logging.INFO)

def main():
    parser = argparse.ArgumentParser(description="Workflow monitor")

    parser.add_argument(
        "-w",
        "--workflow",
        dest="workflow",
        default="carouge",
        help=u"Config file for the workflow. Option values can be:\n  carouge, alicante-consumption, alicante-salinity, braila-consumption, braila-anomaly, braila-state-analysis, braila-leakage-accurate, braila-leakage-approximate."
    )

    # Display help if no arguments are defined
    if (len(sys.argv) == 1 or len(sys.argv) == 2):
        parser.print_help()
        sys.exit(1)

    # Parse input arguments
    args = parser.parse_args()
    workflow = str(args.workflow)

    LOGGER.info("Starting workflow monitoring tool for: %s", workflow)
    wf = Workflow(workflow)
    wf.check()


if (__name__ == '__main__'):
    main()