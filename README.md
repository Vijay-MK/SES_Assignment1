# Software For Embedded System Assignment Group 9

TARUN KUMAR PAMNANI - 2023mt13204@wilp.bits-pilani.ac.in </br>
M K VIJAY - 2024ht01636@wilp.bits-pilani.ac.in</br>
SAYANTIKA CHAKRABORTY SANTANU - 2024ht01622@wilp.bits-pilani.ac.in</br>
BANDE PRATIKSHA ANKUSH - 2024ht01631@wilp.bits-pilani.ac.in  </br>



## Smart Home Energy Monitoring System
This project simulates a Smart Home Energy Monitoring System using a Raspberry Pi and a lightweight Python-based backend. It generates, stores, and visualizes real-time power consumption data for various appliances in a smart home.


### Steps To Run The Project
1. Clone the repository
2. cd smartHomeSystem
3. Source envForSmartHomeSystem/bin/activate
5. Run - python main.py
6. Access the Web Dashboard. Open your browser and navigate to: http://<raspberry-pi-ip>:8000/


### Directory Structure
<pre>
smartHomeSystem/                                                 
├── __pycache__/             # Auto-generated Python cache files
├── envForSmartHomeSystem/   # Python virtual environment for easy setup
├── logs/                    # Log files generated during system operation
├── static/                  # Static files (CSS, JavaScript) for the web dashboard
├── templates/               # HTML templates for the Flask server
├── applicationServer.py     # Flask web server exposing APIs for data access
├── dbInterface.py           # Database interface with retry logic
├── logging.conf             # Logging configuration file
├── main.py                  # Entry point to start server and data generator
├── network_latency.sh       # Script to simulate network latency (optional)
├── requirements.txt         # Python dependencies list
├── sensorDataGenerator.py   # Simulates real-time sensor data for appliances
├── smart_home_mgmt.db       # SQLite database storing appliance data
└── README.md                # Project documentation
</pre>

### Remote Access Setup (For Team Members)
Use hosted Raspberry Pi with remove access at https://connect.raspberrypi.com/devices/ and login with shared credentials.
