import sqlite3
from datetime import datetime, timedelta

class DBInterface:
    def __init__(self, dbName="smart_home_mgmt.db"):
        self.dbName = dbName
        self.initializeDatabase()

    def initializeDatabase(self):
        conn = sqlite3.connect(self.dbName)
        cursor = conn.cursor()
        cursor.execute('DROP TABLE IF EXISTS energyUsage')  # only for clean testing
        cursor.execute('''
            CREATE TABLE energyUsage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                deviceId TEXT NOT NULL,
                applianceName TEXT NOT NULL,
                timeStamp TEXT NOT NULL,
                powerConsumption REAL NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

    def insertData(self, applianceName, powerConsumption, timestamp, deviceId):
        conn = sqlite3.connect(self.dbName)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO energyUsage (deviceId, applianceName, timeStamp, powerConsumption)
            VALUES (?, ?, ?, ?)
        ''', (deviceId, applianceName, timestamp, powerConsumption))
        conn.commit()
        conn.close()


    def fetchLatestEntries(self, limit=100):
        conn = sqlite3.connect(self.dbName)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM energyUsage
            ORDER BY timeStamp DESC
            LIMIT ?
        ''', (limit,))
        rows = cursor.fetchall()
        conn.close()
        return rows

    def getRealTimePowerConsumptionPerDevice(self):
        conn = sqlite3.connect(self.dbName)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT applianceName, SUM(powerConsumption) FROM energyUsage 
            WHERE datetime(timeStamp) >= datetime('now', '-1 minute')
            GROUP BY applianceName
        ''')
        rows = cursor.fetchall()
        conn.close()
        return rows

    def getAveragePowerUsagePerDevice(self):
        conn = sqlite3.connect(self.dbName)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT applianceName, COALESCE(AVG(powerConsumption), 0) FROM energyUsage
            WHERE datetime(timeStamp) >= datetime('now', '-1 day')
            GROUP BY applianceName
        ''')
        rows = cursor.fetchall()
        conn.close()
        return rows

    def getPeakUsagePeriods(self):
        conn = sqlite3.connect(self.dbName)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT strftime('%Y-%m-%d %H:%M:%S', timeStamp), SUM(powerConsumption) as totalPower FROM energyUsage 
            WHERE datetime(timeStamp) >= datetime('now', '-24 hours')
            GROUP BY timeStamp ORDER BY totalPower DESC LIMIT 1
        ''')
        rows = cursor.fetchall()
        conn.close()
        return rows
    
    def getPeakUsagePeriods(self):
        conn = sqlite3.connect(self.dbName)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                strftime('%Y-%m-%d %H:%M:%S', timeStamp) as peak_time,
                ROUND(SUM(powerConsumption), 2) as total_power
            FROM energyUsage 
            WHERE datetime(timeStamp) >= datetime('now', '-24 hours')
            GROUP BY strftime('%Y-%m-%d %H:00', timeStamp)
            ORDER BY total_power DESC 
            LIMIT 1
        ''')
        rows = cursor.fetchall()
        conn.close()
        return rows

    def getHighestPowerConsumingDevice(self, period):
        conn = sqlite3.connect(self.dbName)
        cursor = conn.cursor()
        cursor.execute(f'''
            SELECT applianceName, SUM(powerConsumption) as totalPower FROM energyUsage 
            WHERE datetime(timeStamp) >= datetime('now', '{period}')
            GROUP BY applianceName ORDER BY totalPower DESC LIMIT 1
        ''')
        result = cursor.fetchone()
        conn.close()
        return result if result else (None, 0)

    def getHighestPowerConsumingDevices(self):
        periods = {'-1 day': 'Last 24 Hours', '-7 days': 'Last Week', '-30 days': 'Last Month'}
        results = {}
        for period, label in periods.items():
            results[label] = self.getHighestPowerConsumingDevice(period)
        return results

    def getPowerConsumptionTrend(self):
        conn = sqlite3.connect(self.dbName)
        cursor = conn.cursor()
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

    def getDailyPowerUsageComparison(self):
        conn = sqlite3.connect(self.dbName)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT strftime('%Y-%m-%d', timeStamp) as day, SUM(powerConsumption) FROM energyUsage
            WHERE datetime(timeStamp) >= datetime('now', '-7 days')
            GROUP BY day
            ORDER BY day DESC
        ''')
        rows = cursor.fetchall()
        conn.close()
        return rows

    def clearDatabase(self):
        conn = sqlite3.connect(self.dbName)
        cursor = conn.cursor()
        cursor.execute('''DELETE FROM energyUsage''')
        conn.commit()
        conn.close()
        print("Database cleared successfully.")

    def getAveragePowerTrend(self):
        conn = sqlite3.connect(self.dbName)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                strftime('%H:%M', timeStamp) as hour_slot,
                ROUND(AVG(powerConsumption), 2) as avg_power
            FROM energyUsage 
            WHERE datetime(timeStamp) >= datetime('now', '-24 hours')
            GROUP BY hour_slot
            ORDER BY hour_slot
        ''')
        rows = cursor.fetchall()
        conn.close()
        return rows
        
class ReliableDBInterface(DBInterface):
    def __init__(self, dbName="smart_home_mgmt.db", max_retries=3, retry_delay=1):
        super().__init__(dbName)
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.logger = logging.getLogger(__name__)

    def retry_operation(self, operation, *args, **kwargs):
        for attempt in range(self.max_retries):
            try:
                return operation(*args, **kwargs)
            except sqlite3.OperationalError as e:
                self.logger.warning(f"Attempt {attempt + 1} failed: {e}")
                time.sleep(self.retry_delay)
        self.logger.error(f"All {self.max_retries} retries failed for operation: {operation.__name__}")
        return None

    def insertData(self, applianceName, powerConsumption, timestamp, deviceId):
        return self.retry_operation(super().insertData, applianceName, powerConsumption, timestamp, deviceId)

    def fetchLatestEntries(self, limit=100):
        return self.retry_operation(super().fetchLatestEntries, limit)

    def getRealTimePowerConsumptionPerDevice(self):
        return self.retry_operation(super().getRealTimePowerConsumptionPerDevice)

    def getAveragePowerUsagePerDevice(self):
        return self.retry_operation(super().getAveragePowerUsagePerDevice)

    def getPeakUsagePeriods(self):
        return self.retry_operation(super().getPeakUsagePeriods)

    def getHighestPowerConsumingDevice(self, period):
        return self.retry_operation(super().getHighestPowerConsumingDevice, period)

    def getHighestPowerConsumingDevices(self):
        return self.retry_operation(super().getHighestPowerConsumingDevices)

    def getPowerConsumptionTrend(self):
        return self.retry_operation(super().getPowerConsumptionTrend)

    def getDailyPowerUsageComparison(self):
        return self.retry_operation(super().getDailyPowerUsageComparison)

    def clearDatabase(self):
        return self.retry_operation(super().clearDatabase)

    def getAveragePowerTrend(self):
        return self.retry_operation(super().getAveragePowerTrend)
