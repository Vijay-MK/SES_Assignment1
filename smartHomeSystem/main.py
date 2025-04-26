import os
import argparse
import multiprocessing
import threading
import random
import time
import subprocess
from applicationServer import EnergyMonitorServer

MAIN_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPT_PATH = os.path.join(MAIN_DIR, 'network_latency.sh')
SENSOR_GEN_SCRIPT = os.path.join(MAIN_DIR, 'sensorDataGenerator.py')
SIMULATOR_LOG_FILE = os.path.join(MAIN_DIR, 'logs', 'simulatorLatency.log')

os.makedirs(os.path.join(MAIN_DIR, 'logs'), exist_ok=True)

def log_event(message):
    with open(SIMULATOR_LOG_FILE, 'a') as log:
        log.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")

def start_sensor_data_generator(with_error_handling=False):
    cmd= ["python3", SENSOR_GEN_SCRIPT ]
    if with_error_handling:
        cmd.append("--error_handling_start")
        print(cmd)
    #print("No error handling, normal mode")
    subprocess.run(cmd)

def start_flask_server(enable_retry=False,log_file_path=None):
    if enable_retry and log_file_path:
        # Pass the log file path when retry is enabled
        server = EnergyMonitorServer(
            db_path="smart_home_mgmt.db",
            enable_retry=enable_retry,
            log_file_path=log_file_path
        )
    else:
        # Do not pass the log file path when retry is not enabled
        server = EnergyMonitorServer(
            db_path="smart_home_mgmt.db"
        )
    server.run()

def periodically_apply_network_conditions():
    while True:
        # Reset existing conditions
        subprocess.run(['bash', SCRIPT_PATH, '0', 'reset'])

        mode = random.choice(["delay", "loss"])
        value = random.randint(50, 200) if mode == "delay" else random.randint(1, 10)

        log_event(f"Applying {mode}: {value}")
        subprocess.run(['bash', SCRIPT_PATH, str(value), mode])

        time.sleep(30)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Smart Home Energy Monitor")
    parser.add_argument("--simulator-latency", action="store_true", help="Enable simulated network latency")
    parser.add_argument("--error_handling_start", action="store_true", help="Enable retry and error handling in DB operations")
    args = parser.parse_args()

    log_event("Starting system...")

    # Start sensor data generator in a separate process
    sensor_process = multiprocessing.Process(target=start_sensor_data_generator, args=(args.error_handling_start,))
    sensor_process.start()

    # Delay to ensure DB has some data
    time.sleep(5)

    # Start the Flask server
    start_flask_server()

    # Optional: Start latency simulator
    if args.simulator_latency:
        log_event("Network latency simulation ENABLED")
        net_delay_thread = threading.Thread(target=periodically_apply_network_conditions, daemon=True)
        net_delay_thread.start()
    else:
        log_event("Network latency simulation DISABLED")

    # Optional: Join sensor process if you want to keep main alive
    sensor_process.join()

