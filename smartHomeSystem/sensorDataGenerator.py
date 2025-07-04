import time 
import random
import logging
import sys
import logging.config
from datetime import datetime, timedelta
from dbInterface import DBInterface, ReliableDBInterface

logging.config.fileConfig('logging.conf')
logger = logging.getLogger()

# Decide which DBInterface to use based on CLI arg
use_reliable = '--error_handling_start' in sys.argv
if use_reliable:
    db = ReliableDBInterface("smart_home_mgmt.db")
    logger.info("ReliableDBInterface initialized")
else:
    db = DBInterface("smart_home_mgmt.db")
    logger.info("DBInterface initialized")

def SensorDataGenerator(name, deviceId, timestamp=datetime.now()):
    '''This function generates random sensor data and stores it in the DB.'''
    powerConsumption = random.randint(0, 50)
    timestamp = timestamp.replace(microsecond=0)
    db.insertData(applianceName=name, powerConsumption=powerConsumption, timestamp=timestamp, deviceId=deviceId)
    logger.info(f"Data inserted for {name} with deviceId {deviceId} at {timestamp} into the table")

if __name__ == "__main__":
    # Generate data for different devices for the past 30 days with varying times and dates
        # Include an invalid appliance to trigger error handling
    if '--error_handling_start' in sys.argv:
        Devices = {
            "Smart-AirConditioner": "0001",
            "Smart-WaterHeater": "0002",
            "Smart-Refrigerator": "0003",
            "Smart-WashingMachine": "0004",
            "Invalid-Appliance": "0005"  # Invalid appliance to trigger the error
        }
    else:
        # Normal scenario with only valid devices
        Devices = {
            "Smart-AirConditioner": "0001",
            "Smart-WaterHeater": "0002",
            "Smart-Refrigerator": "0003",
            "Smart-WashingMachine": "0004"
        }

    startDate = datetime.now() - timedelta(days=30)
    endDate = datetime.now()
    currentDate = startDate

    while currentDate <= endDate:
        for devicename, deviceId in Devices.items():
            # Generate a random time for the current date
            random_time = currentDate + timedelta(
                hours=random.randint(0, 23), 
                minutes=random.randint(0, 59), 
                seconds=random.randint(0, 59)
            )
            SensorDataGenerator(devicename, deviceId, random_time)
        currentDate += timedelta(days=1)
        time.sleep(0.1)  # Past data generation should be fast to have live updates reflect in UI

    # Generating the current deviceData after the generation of the past data
    currentDate = datetime.now()
    while True:
        for devicename, deviceId in Devices.items():
            SensorDataGenerator(devicename, deviceId, currentDate)
            currentDate += timedelta(seconds=10)
        time.sleep(5)
