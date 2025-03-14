import sqlite3

def QueryDataForSensor(name):
    con = sqlite3.connect('SensorData.db')
    cursor = con.cursor()
    cursor.execute("SELECT * FROM SensorData WHERE SensorName = ?", (name,))
    data = cursor.fetchall()
    for data in data:
        print(data)


if __name__ == "__main__":
    QueryDataForSensor("Sensor-1")
    
    