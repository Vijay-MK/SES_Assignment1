import os
import multiprocessing
import random
import threading
import time
import subprocess
from applicationServer import EnergyMonitorServer

MAIN_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPT_PATH = os.path.join(MAIN_DIR, 'network_latency.sh')
SENSOR_GEN_SCRIPT = os.path.join(MAIN_DIR, 'sensorDataGenerator.py')

def start_sensor_data_generator():
    subprocess.run(["python3", SENSOR_GEN_SCRIPT])

def start_flask_server():
    server = EnergyMonitorServer(db_path="smart_home_mgmt.db")
    server.run()

def periodically_apply_network_conditions():
    while True:
        delay = random.randint(50, 200)  # ms
        print(f"[Network Emulator] Applying {delay}ms delay.")
        subprocess.run(['bash', SCRIPT_PATH, str(delay)])
        time.sleep(30)  # Change delay every 30 seconds

if __name__ == "__main__":
    # Start sensor data generator in a separate process
    sensor_process = multiprocessing.Process(target=start_sensor_data_generator)
    sensor_process.start()

    # Start network delay simulation in a separate thread(This thread will affect at random times for the multiprocesses)
    #net_delay_thread = threading.Thread(target=periodically_apply_network_conditions, daemon=True)
    #net_delay_thread.start()

    # Delay to ensure DB has some data
    time.sleep(5)

    # Start the Flask server
    start_flask_server()

    # Optional: Join sensor process if you want to keep main alive
    sensor_process.join()

