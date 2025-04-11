import mimetypes
# Prevent mimetypes from reading restricted files.
mimetypes.knownfiles = []
mimetypes.init()

from flask import Flask, render_template, jsonify
from dbInterface import DBInterface

class EnergyMonitorServer:
    def __init__(self, db_path='smart_home_mgmt.db', host='0.0.0.0', port=8000):
        self.app = Flask(__name__)
        self.host = host
        self.port = port
        # Instantiate our DBInterface
        self.db = DBInterface(db_path)
        self.setup_routes()

    def setup_routes(self):
        @self.app.route('/')
        def index():
            return render_template('index.html')

        @self.app.route('/api/latest')
        def api_latest():
            # Using fetchLatestEntries from DBInterface.
            rows = self.db.fetchLatestEntries()
            # Converting tuple results to list of dictionaries.
            latest_entries = [
                    {
                        'applianceName': row[2],
                        'timeStamp': row[3],
                        'powerConsumption': row[4]

                        } for row in rows
                    ]
            return jsonify(latest_entries)

        @self.app.route('/api/real_time')
        def api_real_time():
            rows = self.db.getRealTimePowerConsumptionPerDevice()
            real_time_data = [
                    {
                        'applianceName': row[0],
                        'totalPowerConsumption': row[1]
                        } for row in rows
                    ]
            print(rows)
            print("realtime")
            print(real_time_data)
            return jsonify(real_time_data)

        @self.app.route('/api/average')
        def api_average():
            rows = self.db.getAveragePowerUsagePerDevice()
            print(rows)
            data = [{'applianceName': row[0], 'averagePower': row[1]} for row in rows]
            return jsonify(data)

        @self.app.route('/api/peak')
        def api_peak():
            rows = self.db.getPeakUsagePeriods()
            data = {
                    'peakTime': rows[0][0] if rows else None,
                    'peakPower': rows[0][1] if rows else 0
                    }
            return jsonify(data)

        @self.app.route('/api/highest')
        def api_highest():
            # Returns highest consuming device for various time periods.
            results = self.db.getHighestPowerConsumingDevices()
            data = {
                    period: {
                        'applianceName': result[0] if result else None,
                        'totalPower': result[1] if result else 0
                        } for period, result in results.items()
                    }
            return jsonify(data)

        @self.app.route('/api/trend')
        def api_trend():
            rows = self.db.getPowerConsumptionTrend()
            data = [
                    {'applianceName': row[0], 'hourSlot': row[1], 'totalPower': row[2]}
                    for row in rows
                    ]
            return jsonify(data)

        @self.app.route('/api/daily')
        def api_daily():
            rows = self.db.getDailyPowerUsageComparison()
            data = [{'day': row[0], 'totalPower': row[1]} for row in rows]
            return jsonify(data)
        
        @self.app.route('/api/average_trend')
        def api_average_trend():
            rows = self.db.getAveragePowerTrend()
            data = [
                {
                    'timestamp': row[0],
                    'averagePower': row[1]
                } for row in rows
            ]
            return jsonify(data)

    def run(self):
        self.app.run(host=self.host, port=self.port)


