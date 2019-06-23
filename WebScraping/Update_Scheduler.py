import schedule
import time
import os 

def job():
    os.system('python CIBC_Students.py')
    os.system('python CIBC_Youth.py')
    os.system('RBC_Student_Youth.py')
    os.system('python Scotiabank_Youth.py')
    os.system('python TD_Youth.py')
    os.system('python TD_Student.py')
    os.system('python TD_Regular.py')



schedule.every().monday.at("23:00").do(job)
schedule.every().tuesday.at("23:00").do(job)
schedule.every().wednesday.at("23:00").do(job)
schedule.every().thursday.at("23:00").do(job)
schedule.every().friday.at("23:00").do(job)
schedule.every().saturday.at("23:00").do(job)
schedule.every().sunday.at("23:00").do(job)

while True:
    schedule.run_pending()
    time.sleep(1)