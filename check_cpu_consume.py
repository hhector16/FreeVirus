import psutil
import time
import os
import threading
import json

# This file monitors every file and terminates it in case it exceeds the CPU threshold % configureed in the conf.json and
# the MB of RAM which are also configured in conf.json


# Function to load conf.json and its values to variables

def load_json():
    global cpu_threshold, ram_threshold
    try:
        with open("conf.json","r") as f:
            data = json.load(f)
            cpu_threshold = data["cpu_threshold"]
            ram_threshold = data["ram_threshold"]
    except Exception as e:
        cpu_threshold = 80
        ram_threshold = 300
        print("Error abriendo el archivo: ",e)


# This function reveives a path as parameter and constantly check if it overload the thresholds

def monitor_loop(filepath):
    filepath = os.path.abspath(filepath)
    load_json()
    print(cpu_threshold)
    

    # CPU initialice
    for p in psutil.process_iter():
        try:
            p.cpu_percent(None)
        except:
            pass

    time.sleep(1)

    while True:
        for p in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cpu = p.cpu_percent(None)
                ram = p.memory_info().rss / (1024 * 1024)

                cmdline = " ".join(p.info['cmdline']) if p.info['cmdline'] else ""

                if filepath in cmdline or filepath in p.exe():

                    # if overloads, terminates
                    if cpu > cpu_threshold or ram > ram_threshold:

                        p.terminate() 
                        print("process killed")

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        time.sleep(2)

# Creates a thread so it doesnt block the whole antivirus

def monitor(filepath):
    thread = threading.Thread(
        target=monitor_loop,
        args=(filepath,),
        daemon=True  # exits with main program
    )
    thread.start()
    return thread