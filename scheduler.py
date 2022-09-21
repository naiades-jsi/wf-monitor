import schedule
import time
import analysis
import subprocess
import os
import logging
import json

# logging
LOGGER = logging.getLogger(__name__)

def main(run_time):
    config_file = os.path.join(os.getcwd(), 'configs', 'scheduler.json')
    LOGGER.info("Loading...")
    with open(config_file, "r") as json_file:
        data = json.load(json_file)
        tasks = data['tasks']

    for section in tasks:
        LOGGER.info("Starting: %s", section["name"])
        if run_time == section["scheduledAt"]: #convert to correct data type!!!
            eval(section["command"])

# Run main() every day at every scheduledAt time (find in scheduler.json)
def schedule_job():
    # get all the run times
    times = []
    config_file = os.path.join(os.getcwd(), 'configs', 'scheduler.json')
    with open(config_file, "r") as json_file:
        data = json.load(json_file)
        tasks = data['tasks']
    for section in tasks:
        times.append(section["scheduledAt"])
    
    # schedule job
    for run_time in times:
        schedule.every().day.at(run_time).do(main, run_time=run_time)

schedule_job()

while True:
    schedule.run_pending()
    time.sleep(1)