from utils import *
from os import listdir
from os.path import isfile, join
import datetime
import json

class PlotDataWindow():
    def __init__(self):
        self.report_dir = get_property('REPORT_DIR', 'CONFIG')
        self.report_suffix = get_property('REPORT_FILE', 'CONFIG')
        self.file_time_format = get_property('FILE_TIME', 'CONFIG')
        self.latest_report = self.get_latest_report()
        self.full_report = self.read_report(self.latest_report)
        self.poll_interval = int(get_property('POLLING_INTERVAL', 'SENSOR'))

        self.plot_dir = get_property('PLOT_DATA_DIR', 'CONFIG')
        self.plot_12 = get_property('PLOT_12', 'CONFIG')
        self.plot_24 = get_property('PLOT_24', 'CONFIG')
        self.plot_1W = get_property('PLOT_1W', 'CONFIG')
        self.current = get_property('CURRENT', 'CONFIG')

    def get_latest_report(self):
        reports = [f for f in listdir(self.report_dir) if isfile(join(self.report_dir, f))]
        tail = '-' + self.report_suffix
        dates = map(lambda x: datetime.datetime.strptime(x[0: x.index(tail)], self.file_time_format), reports)
        dates.sort(reverse=True)
        return dates[0].strftime(self.file_time_format) + tail

    def read_report(self, report_file):
        lines = []
        try:
            fd = open(self.report_dir + report_file)
            lines = map(lambda x: x.strip('\n'), fd.readlines())
            fd.close()
        except:
            logging.error('Unable to read report file: %s' % report_file)

        return lines

    def read_latest_report(self):
        self.latest_report = self.get_latest_report()
        self.full_report = self.read_report(self.latest_report)

    def generate_12hr_dataset(self):
        #generate 12 vticks
        last_tuple = self.full_report[len(self.full_report) - 1]
        last_hour = int(last_tuple.split(',')[0].split(':')[0].split('T')[1])
        vticks = [last_hour]
        for i in range(1, 12):
            tick = last_hour - (i)
            vticks.append(tick)
        vticks.sort(reverse=True)

        for i, tick in enumerate(vticks):
            if tick < 0:
                vticks[i] += 24
        vticks = map(lambda x: str(x) + ':00', vticks)
        vticks = map(lambda x: {'v':x + ':00', 'f':x}, vticks)

        self.write_window_data(self.plot_12 + '.json', 43200, vticks)

    def generate_24hr_dataset(self):
        # generate 12 vticks
        last_tuple = self.full_report[len(self.full_report) - 1]
        last_hour = int(last_tuple.split(',')[0].split(':')[0].split('T')[1])
        vticks = [last_hour]
        for i in range(1, 12):
            tick = last_hour - (i * 2)
            vticks.append(tick)
        vticks.sort(reverse=True)

        for i, tick in enumerate(vticks):
            if tick < 0:
                vticks[i] += 24

        vticks = map(lambda x: str(x) + ':00', vticks)
        vticks = map(lambda x: {'v': x + ':00', 'f': x}, vticks)

        self.write_window_data(self.plot_24 + '.json', 86400, vticks)

    def write_window_data(self, filename, window_seconds, vticks):
        # fun math
        data_interval = self.poll_interval
        total_data_points = window_seconds / data_interval

        # 360 data points
        if len(self.full_report) > total_data_points:
            sig_points = self.full_report[len(self.full_report) - total_data_points:]
        else:
            sig_points = self.full_report

        point_gap = int(total_data_points / 360)
        if point_gap < 1:
            point_gap = 1

        plot_list = []
        counter = 1
        for tup in sig_points:
            if counter % point_gap is 0:
                cols = tup.split(',')
                tm = cols[0].split('T')[1]
                plot_list.append([tm, cols[1], cols[2]])

            counter += 1

        data = {
            'v_vticks':vticks,
            'dataset':plot_list
        }

        with open(self.plot_dir + filename, 'w') as json_file:
            json.dump(data, json_file, indent=4)
        logging.info('Wrote %d points to file: %s' % (counter / point_gap, filename))

    def write_current_temps(self, timestamp, s_temp, w_temp):
        data = {
            'timestamp':timestamp,
            'sensor': {'temp_f': s_temp},
            'weather': {'temp_f': w_temp}
        }
        with open(self.plot_dir + self.current + '.json', 'w') as json_file:
            json.dump(data, json_file, indent=4)


