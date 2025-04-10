import sqlite3
from datetime import datetime, timedelta
from contextlib import contextmanager

class DatabaseError(Exception):
    """Base class for database-related exceptions."""

class InsertDataError(DatabaseError):
    """Raised when data insertion fails."""

class FetchDataError(DatabaseError):
    """Raised when data fetch fails."""

class DeviceAnalyticsError(Exception):
    """Raised when power consumption analysis fails."""

def retry_db_operation(retries=3, delay=1.0, exceptions=(sqlite3.OperationalError,)):
    def decorator(func):
        def wrapper(*args, **kwargs):
            attempt = 0
            while attempt < retries:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    attempt += 1
                    if attempt == retries:
                        raise
                    time.sleep(delay)
        return wrapper
    return decorator

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
    
    @retry_db_operation(exceptions=(InsertDataError, sqlite3.OperationalError))
    def insertData(self, applianceName, powerConsumption, timestamp, deviceId):
        try:
            conn = sqlite3.connect(self.dbName)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO energyUsage (deviceId, applianceName, timeStamp, powerConsumption)
                VALUES (?, ?, ?, ?)
             ''', (deviceId, applianceName, timestamp, powerConsumption))
            conn.commit()
        except sqlite3.Error as e:
            raise InsertDataError(f"Failed to insert data for {applianceName} at {timestamp}: {e}")
        finally:
            conn.close()
    
    @contextmanager
    def db_connection(dbName):
        conn = sqlite3.connect(dbName)
        try:
           yield conn
        finally:
           conn.close()

    @retry_db_operation(exceptions=(FetchDataError, sqlite3.OperationalError))
    def fetchLatestEntries(self, limit=100):
    try:
        with db_connection(self.dbName) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM energyUsage
                ORDER BY timeStamp DESC
                LIMIT ?
            ''', (limit,))
            rows = cursor.fetchall()
            return rows
    except sqlite3.Error as e:
        raise FetchDataError(f"Could not fetch latest entries: {e}")

    def getHighestPowerConsumingDevice(self, period):
        try:
            conn = sqlite3.connect(self.dbName)
            cursor = conn.cursor()
            cursor.execute(f'''
                 SELECT applianceName, SUM(powerConsumption) as totalPower FROM energyUsage 
                 WHERE datetime(timeStamp) >= datetime('now', '{period}')
                 GROUP BY applianceName ORDER BY totalPower DESC LIMIT 1
             ''')
            result = cursor.fetchone()
            return result if result else (None, 0)
    
        except sqlite3.OperationalError as e:
            logger.warning(f"[DB OPERATIONAL ERROR] Period: {period} → {e}")
            raise DeviceAnalyticsError(f"Database operational error for period '{period}'") from e
    
        finally:
            conn.close()


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
        print("Database cleared successfully.")
        except sqlite3.Error as e:
            print(f"An error occurred while clearing the database: {e}")
        finally:
            if 'conn' in locals():
            conn.close()

