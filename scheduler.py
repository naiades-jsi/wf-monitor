import schedule
import time
import subprocess
import os
import logging
import json
from datetime import datetime

# logging
LOGGER = logging.getLogger(__name__)

def main(run_time):
    config_file = os.path.join(os.getcwd(), 'configs', 'scheduler.json')
    LOGGER.info("Loading...")
    with open(config_file, "r") as json_file:
        data = json.load(json_file)

    for section in data["tasks"]:
        LOGGER.info("Starting: %s", section["name"])
        if run_time == section["scheduledAt"]: #convert to correct data type!!!
            subprocess.run(section["command"])

            # time of the last data update, write to scheduler.json
            now = datetime.now()
            current_time = now.strftime("%d/%m/%Y %H:%M:%S")
            section["last_update"] = current_time
            with  open(config_file, "w") as outfile:
                json.dump(data, outfile, ensure_ascii=False, indent=4)


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