import schedule
import time
import analysis
import subprocess

# email info
sender_address = '...'
receiver_address = '...'
password ='...'

# at what time?
hh, mm, ss = '...', '...', '...'

def job():
    subprocess.run(['./monitor.sh'])
    analysis.main(sender_address, receiver_address, password)

# Run job every day at specific HH:MM:SS
schedule.every().day.at("hh:mm:ss").do(job)

while True:
    schedule.run_pending()
    time.sleep(1)