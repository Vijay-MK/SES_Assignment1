import time 
import random
import logging
import logging.config
from datetime import datetime, timedelta
from dbInterface import DBInterface


class SensorDataError(Exception):
    """Base exception for sensor data generation issues."""

class TimeGenError(SensorDataError):
    """Raised random time Generation fails."""

logging.config.fileConfig('logging.conf')
logger = logging.getLogger()

db = DBInterface("smart_home_mgmt.db")
logger.info("DBInterface initialized")


def SensorDataGenerator(name, deviceId, timestamp=datetime.now()):
    '''This function generates random sensor data and stores it in the DB.'''
    try:
        powerConsumption = random.randint(0, 50)
        timestamp = timestamp.replace(microsecond=0)
        db.insertData(applianceName=name, powerConsumption=powerConsumption, timestamp=timestamp, deviceId=deviceId)
        logger.info(f"Data inserted for {name} with deviceId {deviceId} at {timestamp} into the table")
    except Exception as data_error:
        error_context = {
                "function": "SensorDataGenerator",
                "deviceId": deviceId,
                "applianceName": name,
                "timestamp": timestamp,
                "errorType": type(data_error).__name__,
                "message": str(data_error)
            }
        raise DatabaseInsertError(f"[ERROR] {error_context}", exc_info=True)

if __name__ == "__main__":
    # Generate data for different devices for the past 30 days with varying times and dates
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
            try:

                random_time = currentDate + timedelta(
                  hours=random.randint(0, 23), 
                  minutes=random.randint(0, 59), 
                  seconds=random.randint(0, 59)
                  )
                SensorDataGenerator(devicename, deviceId, random_time)
            except TimeGenError as randomgen_error:
                logger.warning(f'Skipped device {devicename} on {currentDate.date()} due to error:{randomgen_error}') 
                
                try:
                  fallback_time = currentDate.replace(hour=12, minute=0, second=0, microsecond=0)
                  SensorDataGenerator(devicename, deviceId, fallback_time)
                  logger.info(f"Fallback insertion successful for {devicename} using current time {fallback_time}")
                
                except TimeGenError as fallback_error:
                  logger.error(f"Fallback also failed for {devicename}: {fallback_error}", exc_info=True)
        
        currentDate += timedelta(days=1)
        time.sleep(0.1)  # Past data generation should be fast to have live updates reflect in UI

    # Generating the current deviceData after the generation of the past data
    currentDate = datetime.now()
    while True:
        for devicename, deviceId in Devices.items():
            SensorDataGenerator(devicename, deviceId, currentDate)
            currentDate += timedelta(seconds=10)
        time.sleep(5)
