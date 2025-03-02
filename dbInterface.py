import sqlite3
from datetime import datetime, timedelta

def initializeDatabase(dbName):
    conn = sqlite3.connect(dbName)
    cursor = conn.cursor()
    
    # Create table if it doesn't exist with timeStamp in readable format
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS energyUsage (
            deviceId INTEGER PRIMARY KEY AUTOINCREMENT,
            applianceName TEXT NOT NULL,
            timeStamp TEXT NOT NULL,
            powerConsumption REAL NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

def insertData(dbName, applianceName, powerConsumption, timestamp):
    conn = sqlite3.connect(dbName)
    cursor = conn.cursor()
    
    # Insert a new energy usage record into the table
    cursor.execute('''
        INSERT INTO energyUsage (applianceName, timeStamp, powerConsumption)
        VALUES (?, ?, ?)
    ''', (applianceName, timestamp, powerConsumption))
    
    conn.commit()
    conn.close()

def fetchLatestEntries(dbName, limit=100):
    conn = sqlite3.connect(dbName)
    cursor = conn.cursor()
    
    # Retrieve the latest entries sorted by timestamp
    cursor.execute('''
        SELECT * FROM energyUsage
        ORDER BY datetime(timeStamp) DESC
        LIMIT ?
    ''', (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    return rows

def getRealTimePowerConsumptionPerDevice(dbName):
    conn = sqlite3.connect(dbName)
    cursor = conn.cursor()
    
    # Fetch real-time power consumption per device in the last minute
    cursor.execute('''
        SELECT applianceName, SUM(powerConsumption) FROM energyUsage 
        WHERE datetime(timeStamp) >= datetime('now', '-1 minute')
        GROUP BY applianceName
    ''')
    
    rows = cursor.fetchall()
    conn.close()
    return rows

def getAveragePowerUsagePerDevice(dbName):
    conn = sqlite3.connect(dbName)
    cursor = conn.cursor()
    
    # Compute the average power consumption per device in the last 24 hours
    cursor.execute('''
        SELECT applianceName, COALESCE(AVG(powerConsumption), 0) FROM energyUsage
        WHERE datetime(timeStamp) >= datetime('now', '-1 day')
        GROUP BY applianceName
    ''')
    
    rows = cursor.fetchall()
    conn.close()
    return rows

def getPeakUsagePeriods(dbName):
    conn = sqlite3.connect(dbName)
    cursor = conn.cursor()
    
    # Retrieve the peak usage period with the highest power consumption in the last 24 hours
    cursor.execute('''
        SELECT strftime('%Y-%m-%d %H:%M:%S', timeStamp), SUM(powerConsumption) as totalPower FROM energyUsage 
        WHERE datetime(timeStamp) >= datetime('now', '-24 hours')
        GROUP BY timeStamp ORDER BY totalPower DESC LIMIT 1
    ''')
    
    rows = cursor.fetchall()
    conn.close()
    return rows

def getHighestPowerConsumingDevice(dbName, period):
    conn = sqlite3.connect(dbName)
    cursor = conn.cursor()
    
    # Identify the highest power-consuming device for a given time period
    cursor.execute(f'''
        SELECT applianceName, SUM(powerConsumption) as totalPower FROM energyUsage 
        WHERE datetime(timeStamp) >= datetime('now', '{period}')
        GROUP BY applianceName ORDER BY totalPower DESC LIMIT 1
    ''')
    
    result = cursor.fetchone()
    conn.close()
    return result if result else (None, 0)

def getHighestPowerConsumingDevices(dbName):
    periods = {'-1 day': 'Last 24 Hours', '-7 days': 'Last Week', '-30 days': 'Last Month'}
    results = {}
    for period, label in periods.items():
        results[label] = getHighestPowerConsumingDevice(dbName, period)
    return results

def getPowerConsumptionTrend(dbName):
    conn = sqlite3.connect(dbName)
    cursor = conn.cursor()
    
    # Retrieves power consumption trends for each device over the last 24 hours at hourly intervals
    cursor.execute('''
        SELECT applianceName, strftime('%Y-%m-%d %H:00:00', timeStamp) as hourSlot, 
               SUM(powerConsumption) FROM energyUsage 
        WHERE datetime(timeStamp) >= datetime('now', '-24 hours')
        GROUP BY applianceName, hourSlot
        ORDER BY hourSlot
    ''')
    
    rows = cursor.fetchall()
    conn.close()
    return rows


def getDailyPowerUsageComparison(dbName):
    conn = sqlite3.connect(dbName)
    cursor = conn.cursor()
    
    # Retrieves daily power usage for the last 7 days
    cursor.execute('''
        SELECT strftime('%Y-%m-%d', timeStamp) as day, SUM(powerConsumption) FROM energyUsage
        WHERE datetime(timeStamp) >= datetime('now', '-7 days')
        GROUP BY day
        ORDER BY day DESC
    ''')
    
    rows = cursor.fetchall()
    conn.close()
    return rows

  
def clearDatabase(dbName):
    conn = sqlite3.connect(dbName)
    cursor = conn.cursor()
    
    # Deletes all records from the energyUsage table
    cursor.execute('''DELETE FROM energyUsage''')
    
    conn.commit()
    conn.close()
    print("Database cleared successfully.")

if __name__ == "__main__":
    
    dbName = "smart_home_mgmt.db"
    
    initializeDatabase(dbName)
    
    # Simulate real-world usage of multiple devices with timestamps across different time ranges
    devices = [
        ("Smart Washing Machine", 500.0),
        ("Smart Refrigerator", 200.0),
        ("Smart LED Bulb", 10.0)
    ]
    
    now = datetime.now()
    timeOffsets = [0, -6, -12, -24, -48, -168, -720]  # Hours spread over different periods
    powerOffset = 50.0  # Incremental power offset per time interval
    
    for device, basePower in devices:
        for i, offset in enumerate(timeOffsets):
            timestamp = (now + timedelta(hours=offset)).strftime('%Y-%m-%d %H:%M:%S')
            power = basePower + (i * powerOffset)  # Vary power over time
            insertData(dbName, device, power, timestamp)

    # Query1: Allows users to see the latest entries for power consumption
    print("Latest Entries:")
    for row in fetchLatestEntries(dbName):
        print(row)

    # Query2: Allows users to see real-time power consumption per device in the last minute
    print("\nReal-Time Power Consumption (Last 1 Minute) per Device:")
    for device, power in getRealTimePowerConsumptionPerDevice(dbName):
        print(f"{device}: {power} Watts")

    # Query3: Allows users to see the average power consumption per device in the last 24 hours
    print("\nAverage Power Usage Per Device (Last 24 Hours):")
    for device, avgPower in getAveragePowerUsagePerDevice(dbName):
        print(f"{device}: {avgPower} Watts")

    # Query4: Allows users to see the highest total power consumption time period in the last 24 hours
    print("\nPeak Usage Period (Last 24 Hours):")
    for row in getPeakUsagePeriods(dbName):
        print(row)

    # Query5: Allows users to see the appliance with the highest power consumption in various time periods
    print("\nHighest Power Consuming Devices:")
    for label, (highestDevice, highestPower) in getHighestPowerConsumingDevices(dbName).items():
        print(f"{label}: {highestDevice} with {highestPower} Watts")

   # Query6: Allows users to see power consumption trends per device over the last 24 hours at hourly intervals (plot graph)
    print("\nPower Consumption Trend (Last 24 Hours - Hourly):")
    for row in getPowerConsumptionTrend(dbName):
        print(row)

    # Query7: Allows users to see daily power usage comparison for the last 7 days (plot graph)
    print("\nDaily Power Usage Comparison (Last 7 Days):")
    for row in getDailyPowerUsageComparison(dbName):
        print(row)

      
    clearDatabase(dbName)

