import schedule
import time
import analysis
import subprocess

# email info
sender_address = '...'
receiver_address = '...'
password ='...'

# at what time (HH:MM:SS format)?
run_time = '...' 

def job():
    subprocess.run(['./monitor.sh'])
    analysis.main(sender_address, receiver_address, password)

# Run job every day at specific HH:MM:SS
schedule.every().day.at(run_time).do(job)

while True:
    schedule.run_pending()
    time.sleep(1)