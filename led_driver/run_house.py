import subprocess
import signal
import sys

def signal_handler(sig, frame):
    print('Stopping all processes...')
    for process in processes:
        process.terminate()
    sys.exit(0)

ips = ["10.10.10.78", "10.10.10.151", "10.10.10.152", "10.10.10.154", "10.10.10.155"]
processes = []

for ip in ips:
    command = f"/home/frank/development/lightboard/led_driver/venv/bin/python /home/frank/development/lightboard/led_driver/house.py {ip}"
    processes.append(subprocess.Popen(command, shell=True))

signal.signal(signal.SIGINT, signal_handler)

# Keep the script running
signal.pause()
