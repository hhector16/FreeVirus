import psutil
import time
import json
import os

cpu_threshold = 180
ram_threshold = 3000  # MB

over_limit_time = {}

my_pid = os.getpid()


# Load thresholds from conf.json
def load_json():
    global cpu_threshold, ram_threshold

    try:
        with open("conf.json", "r") as f:
            data = json.load(f)

            cpu_threshold = float(data.get("cpu_threshold", 180))
            ram_threshold = float(data.get("ram_threshold", 3000))

    except Exception as e:
        print(f"[ERROR] conf.json: {e}")


# Avoid killing critical Linux processes
def is_safe_process(name, pid):
    if not name:
        return True

    name = name.lower()

    critical = [
        "systemd",
        "init",
        "dbus",
        "networkmanager",
        "polkit",
        "snapd",
        "login",
        "sshd",
        "cron",
        "bash",
        "zsh",
        "sudo",
        "python"
    ]

    # Never kill low system PIDs
    if pid < 100:
        return True

    return any(c in name for c in critical)


# Main monitoring loop
def monitor_loop():
    load_json()

    print(f"[INFO] CPU Threshold: {cpu_threshold}%")
    print(f"[INFO] RAM Threshold: {ram_threshold} MB")

    # Initialize CPU measurement
    for p in psutil.process_iter():
        try:
            p.cpu_percent(None)
        except Exception:
            pass

    time.sleep(1)

    while True:
        now = time.time()

        for p in psutil.process_iter(['pid', 'name']):
            try:
                pid = p.info['pid']
                name = p.info.get('name', '')

                # Never kill this script
                if pid == my_pid:
                    continue

                # Skip critical processes
                if is_safe_process(name, pid):
                    continue

                # CPU usage
                cpu = p.cpu_percent(None)

                # Better memory measurement on Linux
                try:
                    ram = p.memory_full_info().uss / (1024 * 1024)
                except Exception:
                    ram = p.memory_info().rss / (1024 * 1024)

                over = (
                    cpu > cpu_threshold or
                    ram > ram_threshold
                )

                if over:

                    if pid not in over_limit_time:
                        over_limit_time[pid] = now

                    else:
                        # Kill after 1 second over limit
                        if now - over_limit_time[pid] >= 1:
                            print(
                                f"[KILL] PID={pid} ({name})"
                            )

                            try:
                                p.kill()
                                print(
                                    f"[KILLED] PID={pid}"
                                )

                            except Exception as e:
                                print(
                                    f"[ERROR KILLING] "
                                    f"PID={pid}: {e}"
                                )

                            over_limit_time.pop(pid, None)

                else:
                    over_limit_time.pop(pid, None)

            except (
                psutil.NoSuchProcess,
                psutil.AccessDenied
            ):
                over_limit_time.pop(pid, None)

            except Exception as e:
                print(f"[ERROR] {e}")

        time.sleep(1)
