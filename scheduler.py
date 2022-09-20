import schedule
import time
import analysis
import subprocess
import os
import logging
import json

# email info
sender_address = '...'
receiver_address = '...'
password ='...'

# logging
LOGGER = logging.getLogger(__name__)
def main():
    config_file = os.path.join(os.getcwd(), 'configs', 'scheduler.json')
    LOGGER.info("Loading...")
    with open(config_file, "r") as json_file:
        data = json.load(json_file)
        tasks = data['tasks']

    for section in tasks:
        LOGGER.info("Starting checks for: %s", section["name"])



# at what time (HH:MM:SS format)?
#run_time = '...' 

#def job():
#    subprocess.run(['./monitor.sh'])
#    analysis.main(sender_address, receiver_address, password)

# Run job every day at specific HH:MM:SS
#schedule.every().day.at(run_time).do(job)

#while True:
#    schedule.run_pending()
#    time.sleep(1)