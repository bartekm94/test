#!/usr/bin/env python3
import subprocess
import sys
from datetime import datetime

LOG_FILE = "/var/log/docker_cleanup_daily.log"

def run_command(cmd):
    try:
        result = subprocess.run(cmd, shell=True, check=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout.strip().splitlines()
    except subprocess.CalledProcessError:
        return []

def get_today():
    return datetime.now().strftime("%Y-%m-%d")

def read_counter():
    try:
        with open(LOG_FILE, "r") as f:
            line = f.readline().strip()
            if line:
                day, count = line.split()
                return day, int(count)
    except FileNotFoundError:
        pass
    return get_today(), 0

def write_counter(day, count):
    with open(LOG_FILE, "w") as f:
        f.write(f"{day} {count}\n")

def cleanup_containers():
    day, count = read_counter()
    today = get_today()

    if day != today:
        day = today
        count = 0

    exited_containers = run_command("docker ps -a -q -f status=exited")
    removed = len(exited_containers)

    if removed > 0:
        run_command("docker rm $(docker ps -a -q -f status=exited)")
        count += removed
        write_counter(today, count)
        print(f"Usunięto {removed} kontenerów. Dzisiaj razem: {count}")
        sys.exit(0)
    else:
        print(f"Brak nowych zatrzymanych kontenerów. Dzisiaj razem: {count}")
        sys.exit(0)

if __name__ == "__main__":
    cleanup_containers()

