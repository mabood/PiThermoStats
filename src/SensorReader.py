from utils import *
import datetime

class SensorReader():
    def __init__(self):
        self.device_dir = get_property('DEVICES_DIR', 'SENSOR')
        self.device_name = get_property('DEVICE_NAME', 'SENSOR')
        self.slave_file = get_property('REPORT_FILE', 'SENSOR')
        self.timestamp_format = get_property('TIME_FORMAT', 'CONFIG')
        self.full_path = self.device_dir + self.device_name + '/' + self.slave_file

        self.latest_measurement_time, self.latest_temp_c = self.measure_temp_c()
        self.latest_temp_f = self.convert_c_to_f(self.latest_temp_c)

    def read_slave_file(self):
        try:
            fd = open(self.full_path, 'r')
            return fd.read()

        except IOError as e:
            logging.error(e.message)
            return None

    def measure_temp_c(self):
        slave_data = self.read_slave_file()
        timestamp = datetime.datetime.now().strftime(self.timestamp_format)
        if slave_data:
            temp_c = slave_data[slave_data.index('t=') + 2:]
            temp_c = int(temp_c.strip('\n'))
            temp_c = float(temp_c) / 1000
            return timestamp, temp_c
        else:
            logging.error('Unable to parse temp - fd is None')

    def convert_c_to_f(self, temp_c):
        return (temp_c * 1.8) + 32

    def poll_sensor_and_update(self):
        self.latest_measurement_time, self.latest_temp_c = self.measure_temp_c()
        self.latest_temp_f = self.convert_c_to_f(self.latest_temp_c)

