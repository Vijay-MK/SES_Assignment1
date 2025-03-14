import sqlite3
import time 
import random
import logging
import logging.config

logging.config.fileConfig('logging.conf')
logger = logging.getLogger()
conn = sqlite3.connect("SensorData.db")
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS SensorData (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    PowerConsumed INTEGER,
                   SensorName TEXT NOT NULL,
                   timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
logger.info("Table created")
conn.commit()

def SensorDataGenerator(name):
    '''SensorDataGenerator is a function that generates random sensor data and stores it in the DB.'''
    '''Arguments: name - name of the sensor, DBname - Name of the Database.'''
    powerConsumed = random.randint(0,50)
    cursor.execute('''INSERT INTO SensorData (SensorName , PowerConsumed) VALUES (?, ?)''', (name, powerConsumed))
    conn.commit()
    logger.info("Data inserted into the table")

if __name__ == "__main__":
    while True:
        SensorDataGenerator("Sensor-1")
        time.sleep(5)
        SensorDataGenerator("Sensor-2")
        time.sleep(5)
        

