import psutil
import time
import json
import os

cpu_threshold = 180
ram_threshold = 3000

over_limit_time = {}

my_pid = os.getpid()

# This file verifies every existing process and compares it to the thresholds
# If the CPU% or RAM are higher than the thresholds the process is killed

# Function which gets the value of the json file
def load_json():
    global cpu_threshold, ram_threshold
    try:
        with open("conf.json", "r") as f:
            data = json.load(f)
            cpu_threshold = float(data.get("cpu_threshold", 80))
            ram_threshold = float(data.get("ram_threshold", 300))
    except Exception as e:
        cpu_threshold = 80
        ram_threshold = 300
        print("Error abriendo conf.json:", e)

# This function avoid killing critical process
def is_safe_process(name):
    if not name:
        return False

    name = name.lower()

    critical = [
        "system", "idle", "explorer", "kernel", "wininit",
        "services", "csrss", "svchost"
    ]

    return any(c in name for c in critical)

# Main function which monitors every process
def monitor_loop():
    load_json()

    for p in psutil.process_iter():
        try:
            p.cpu_percent(None)
        except:
            pass

    time.sleep(1)

    while True:
        now = time.time()

        for p in psutil.process_iter(['pid', 'name']):
            try:
                pid = p.info['pid']
                name = p.info.get('name', '')

                if pid == my_pid:
                    continue

                if is_safe_process(name):
                    continue

                cpu = p.cpu_percent(None)
                ram = p.memory_info().rss / (1024 * 1024)

                over = cpu > cpu_threshold or ram > ram_threshold

                if over:
                    if pid not in over_limit_time:
                        over_limit_time[pid] = now
                    else:
                        if now - over_limit_time[pid] >= 5:
                            print(f"Terminando PID={pid} ({name})")

                            try:
                                p.terminate()
                                p.wait(timeout=3)
                                print(f"PID={pid} terminado")
                            except psutil.TimeoutExpired:
                                print(f"PID={pid} forzado kill")
                                p.kill()
                            except Exception:
                                pass

                            over_limit_time.pop(pid, None)
                else:
                    over_limit_time.pop(pid, None)

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                over_limit_time.pop(pid, None)
            except Exception:
                pass

        time.sleep(3)  
