import sqlite3

class viewData:
    def __init__(self, dbName):
        self.dbName = dbName
        self.conn = sqlite3.connect(dbName)
        self.cursor = self.conn.cursor()
    def fetchLatestEntries(self,limit=100):
        conn = sqlite3.connect(self.dbName)
        cursor = conn.cursor()
    
        # Retrieve the latest entries sorted by timestamp
        cursor.execute('''
        SELECT * FROM SensorData
        ORDER BY dateTime(timeStamp) DESC
        LIMIT ?
        ''', (limit,))
    
        rows = cursor.fetchall()
        conn.close()
        return rows

    def getRealTimePowerConsumptionPerDevice(self):
        conn = sqlite3.connect(self.dbName)
        cursor = conn.cursor()
    
        # Fetch real-time power consumption per device in the last minute
        cursor.execute('''
        SELECT SensorName, SUM(PowerConsumed) FROM SensorData 
        WHERE datetime(timeStamp) >= datetime('now', '-1 minute')
        GROUP BY SensorName
        ''')
    
        rows = cursor.fetchall()
        conn.close()
        return rows

    def getAveragePowerUsagePerDevice(Self):
        conn = sqlite3.connect(Self.dbName)
        cursor = conn.cursor()
    
        # Compute the average power consumption per device in the last 24 hours
        cursor.execute('''
        SELECT SensorName, COALESCE(AVG(powerConsumption), 0) FROM SensorData
        WHERE datetime(timeStamp) >= datetime('now', '-1 day')
        GROUP BY SensorName
        ''')
    
        rows = cursor.fetchall()
        conn.close()
        return rows

    def getPeakUsagePeriods(Self):
        conn = sqlite3.connect(Self.dbName)
        cursor = conn.cursor()
    
    # Retrieve the peak usage period with the highest power consumption in the last 24 hours
        cursor.execute('''
        SELECT strftime('%Y-%m-%d %H:%M:%S', timeStamp), SUM(powerConsumption) as totalPower FROM SensorData 
        WHERE datetime(timeStamp) >= datetime('now', '-24 hours')
        GROUP BY timeStamp ORDER BY totalPower DESC LIMIT 1
        ''')
    
        rows = cursor.fetchall()
        conn.close()
        return rows

    def getHighestPowerConsumingDevice(Self, period):
        conn = sqlite3.connect(Self.dbName)
        cursor = conn.cursor()
    
    # Identify the highest power-consuming device for a given time period
        cursor.execute(f'''
        SELECT applianceName, SUM(powerConsumption) as totalPower FROM SensorData 
        WHERE datetime(timeStamp) >= datetime('now', '{period}')
        GROUP BY applianceName ORDER BY totalPower DESC LIMIT 1
        ''')
    
        result = cursor.fetchone()
        conn.close()
        return result if result else (None, 0)

    def getHighestPowerConsumingDevices(Self):
        periods = {'-1 day': 'Last 24 Hours', '-7 days': 'Last Week', '-30 days': 'Last Month'}
        results = {}
        for period, label in periods.items():
            results[label] = Self.getHighestPowerConsumingDevice(Self.dbName, period)
        return results

    def getPowerConsumptionTrend(Self):
        conn = sqlite3.connect(Self.dbName)
        cursor = conn.cursor()
    
    # Retrieves power consumption trends for each device over the last 24 hours at hourly intervals
        cursor.execute('''
            SELECT applianceName, strftime('%Y-%m-%d %H:00:00', timeStamp) as hourSlot, 
               SUM(powerConsumption) FROM SensorData 
            WHERE datetime(timeStamp) >= datetime('now', '-24 hours')
            GROUP BY applianceName, hourSlot
            ORDER BY hourSlot
        ''')
    
        rows = cursor.fetchall()
        conn.close()
        return rows


    def getDailyPowerUsageComparison(Self):
        conn = sqlite3.connect(Self.dbName)
        cursor = conn.cursor()
    
    # Retrieves daily power usage for the last 7 days
        cursor.execute('''
            SELECT strftime('%Y-%m-%d', timeStamp) as day, SUM(powerConsumption) FROM SensorData
            WHERE datetime(timeStamp) >= datetime('now', '-7 days')
            GROUP BY day
            ORDER BY day DESC
        ''')
    
        rows = cursor.fetchall()
        conn.close()
        return rows

  
    def clearDatabase(Self):
        conn = sqlite3.connect(Self.dbName)
        cursor = conn.cursor()
    
        # Deletes all records from the SensorData table
        cursor.execute('''DELETE FROM SensorData''')
    
        conn.commit()
        conn.close()
        print("Database cleared successfully.")


if __name__ == "__main__":
    view =viewData("SensorData.db")
    
