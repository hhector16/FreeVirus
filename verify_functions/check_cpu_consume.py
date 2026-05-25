import psutil
import time
import json

cpu_threshold = 80
ram_threshold = 300


def load_json():
    global cpu_threshold, ram_threshold
    try:
        with open("conf.json","r") as f:
            data = json.load(f)
            cpu_threshold = float(data["cpu_threshold"])
            ram_threshold = float(data["ram_threshold"])
    except Exception as e:
        cpu_threshold = 80
        ram_threshold = 300
        print("Error abriendo el archivo:", e)


def monitor_loop():
    load_json()

    # inicialización de CPU measurement
    for p in psutil.process_iter():
        try:
            p.cpu_percent(None)
        except:
            pass

    time.sleep(1)

    while True:
        for p in psutil.process_iter(['pid', 'name']):
            try:
                cpu = p.cpu_percent(None)
                ram = p.memory_info().rss / (1024 * 1024)

                if cpu > cpu_threshold or ram > ram_threshold:
                    p.terminate()
                    print(f"Process killed PID={p.pid}")

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        time.sleep(2)