import multiprocessing
import time
import subprocess
from applicationServer import EnergyMonitorServer

def start_sensor_data_generator():
    subprocess.run(["python3", "sensorDataGenerator.py"])

def start_flask_server():
    server = EnergyMonitorServer(db_path="smart_home_mgmt.db")
    server.run()

if __name__ == "__main__":
    # Start sensor data generator in a separate process
    sensor_process = multiprocessing.Process(target=start_sensor_data_generator)
    sensor_process.start()

    # Delay to ensure DB has some data
    time.sleep(5)

    # Start the Flask server
    start_flask_server()

    # Optional: Join sensor process if you want to keep main alive
    sensor_process.join()

