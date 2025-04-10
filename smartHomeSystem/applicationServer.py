import mimetypes
import logging
# Prevent mimetypes from reading restricted files.
mimetypes.knownfiles = []
mimetypes.init()

from flask import Flask, render_template, jsonify
from dbInterface import DBInterface

os.makedirs('logs', exist_ok=True)

# Configure logging
logging.basicConfig(
    filename='logs/app.log',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

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
            try:
                return render_template('index.html'
                        )
            except Exception as e:
                logger.error(f"Error rendering index page: {e}")
                return jsonify({'error': 'Internal server error'}), 500
        
        @self.app.route('/api/latest')
        def api_latest():
            try:
                rows = self.db.fetchLatestEntries()
                latest_entries = [
                    {
                        'applianceName': row[2],
                        'timeStamp': row[3],
                        'powerConsumption': row[4]
                    } for row in rows
                ]
                logger.info("Fetched latest entries..")
                return jsonify(latest_entries)

            except Exception as e:
                logger.error(f"Error fetching latest entries: {e}")
                return jsonify({'error': 'Failed to fetch latest data'}), 500


        @self.app.route('/api/real_time')
        def api_real_time():
            try:
                rows = self.db.getRealTimePowerConsumptionPerDevice()
                real_time_data = [
                    {
                        'applianceName': row[0],
                        'totalPowerConsumption': row[1]
                    } for row in rows
                  ]
                logger.info("Fetched real-time power consumption.")
                print(rows)
                print("realtime")
                print(real_time_data)
                return jsonify(real_time_data)
            except Exception as e:
                logger.error(f"Error fetching real-time data: {e}")
                return jsonify({'error': 'Failed to fetch real-time data'}), 500


        @self.app.route('/api/average')
        def api_average():
            try:
                rows = self.db.getAveragePowerUsagePerDevice()
                print(rows)
                data = [{'applianceName': row[0], 'averagePower': row[1]} for row in rows]
                logger.info("Fetched average power usage.")
                return jsonify(data)
            except Exception as e:
                logger.error(f"Error fetching average power usage: {e}")
                return jsonify({'error': 'Failed to fetch average data'}), 500

        @self.app.route('/api/peak')
        def api_peak():
            try:
                rows = self.db.getPeakUsagePeriods()
                data = {
                        'peakTime': rows[0][0] if rows else None,
                        'peakPower': rows[0][1] if rows else 0
                    }
                logger.info("Fetched peak usage data.")
                return jsonify(data)
            except Exception as e:
                logger.error(f"Error fetching peak usage data: {e}")
                return jsonify({'error': 'Failed to fetch peak data'}), 500

        @self.app.route('/api/highest')
        def api_highest():
            # Returns highest consuming device for various time periods.
            try:
                results = self.db.getHighestPowerConsumingDevices()
                data = {
                    period: {
                        'applianceName': result[0] if result else None,
                        'totalPower': result[1] if result else 0
                        } for period, result in results.items()
                    }
                logger.info("Fetched highest power consuming devices.")
                return jsonify(data)
            except Exception as e:
                logger.error(f"Error fetching highest devices: {e}")
                return jsonify({'error': 'Failed to fetch highest device data'}), 500

        @self.app.route('/api/trend')
        def api_trend():
            try:
                rows = self.db.getPowerConsumptionTrend()
                data = [
                      {'applianceName': row[0], 'hourSlot': row[1], 'totalPower': row[2]}
                      for row in rows
                    ]
                logger.info("Fetched power consumption trend.")
                return jsonify(data)
            except Exception as e:
                logger.error(f"Error fetching trend data: {e}")
                return jsonify({'error': 'Failed to fetch trend data'}), 500

        @self.app.route('/api/daily')
        def api_daily():
            try:
                rows = self.db.getDailyPowerUsageComparison()
                data = [{'day': row[0], 'totalPower': row[1]} for row in rows]
                logger.info("Fetched daily power usage.")
                return jsonify(data)
            except Exception as e:
                logger.error(f"Error fetching daily power usage: {e}")
                return jsonify({'error': 'Failed to fetch daily data'}), 500

    def run(self):
        self.app.run(host=self.host, port=self.port)


