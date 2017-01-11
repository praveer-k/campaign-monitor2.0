import os, datetime, subprocess

working_directory = "./data/"
todays_date = datetime.datetime.now().strftime("%Y-%m-%d")
for root, dirs, files in os.walk(working_directory):
    for d in dirs:
        creation_time = os.stat(os.path.join(root, d)).st_ctime
        creation_date = datetime.datetime.fromtimestamp(creation_time).strftime("%Y-%m-%d")
        if todays_date==creation_date:
            print(todays_date, creation_date, True)
            try:
                new_process = subprocess.Popen("python run.py "+d, shell=True)
                print(new_process.pid)
            except Exception as e:
                print("Error :",e)
        else:
            print(todays_date, creation_date, False)
