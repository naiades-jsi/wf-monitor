import os
import json
import time
import logging
import requests
import schedule
import subprocess
from datetime import datetime

# logging
LOGGER = logging.getLogger(__name__)
logging.basicConfig(
    format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s", level=logging.INFO)


def ping():
    ping_response = requests.get('https://betteruptime.com/api/v1/heartbeat/wkndZC6mD8MSTm2bN27hNwXz')
    LOGGER.info("Ping to betteruptime was sent. Received reponse with status code " + str(ping_response.status_code))


def main(run_time):
    # open json (get data)
    config_file = os.path.join(os.getcwd(), 'config', 'scheduler.json')
    LOGGER.info("Loading ...")
    with open(config_file, "r") as json_file:
        data = json.load(json_file)

    # read one task at a time
    for section in data["tasks"]:
        LOGGER.info("Starting: %s", section["name"])
        # if scheduled at the time, call command (to update data)
        if run_time == section["scheduledAt"]:
            if section["name"] != 'analysis':
                file_loc = os.path.join(os.getcwd(), 'logs', f'{section["name"]}.log')
                with open(file_loc, "wb") as out:
                    subprocess.Popen(section["command"], shell=True, stdout=out, stderr=out)
            # if the task is analysis, analysis.py is run (gather all the data, and send an email)
            elif section["name"] == 'analysis':
                time.sleep(30)
                subprocess.Popen(section["command"], shell=True)

            # write the time of the last data update to scheduler.json
            now = datetime.now()
            current_time = now.strftime("%d/%m/%Y %H:%M:%S")
            section["last_update"] = current_time

    # update json
    with open(config_file, "w") as outfile:
        json.dump(data, outfile, ensure_ascii=False, indent=4)


# schedule (find in scheduler.json)
def schedule_job():
    # get all the run times
    times = []
    config_file = os.path.join(os.getcwd(), 'config', 'scheduler.json')
    with open(config_file, "r") as json_file:
        data = json.load(json_file)
        tasks = data['tasks']
    for section in tasks:
        times.append(section["scheduledAt"])
    # times = ["00:00", "01:00", "02:00", "03:00", "04:00", "05:00", "06:00", "07:00", "08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00", "21:00", "22:00", "23:00"]
    # schedule job
    for run_time in times:
        schedule.every().day.at(run_time).do(main, run_time=run_time)

    # add ping job to be executed every 5 minutes
    schedule.every(5).minutes.do(ping)


LOGGER.info("WF monitor started")
schedule_job()

# Run main() every day at every scheduledAt time
while True:
    schedule.run_pending()
    time.sleep(1)
