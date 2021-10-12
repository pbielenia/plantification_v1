import argparse
import csv
import datetime as dt
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np

'''
todo:
    - Get rid of passing `measured_value` and getting it from a file name.
    - Touch up plot. - details needed
    - Add some enums, eg. as device type (sensor (+humidity, temperature), lamp, fan)
'''


def main():
    try:
        args = parse_input_args()
        plot_data_creator = PlotDataCreator()

        print('-- Arguments parsed')

        for file in args.files:
            print('-- Reading data from file \"{}\"'.format(file))
            plot_data_creator.read_csv_file(file)
            print('-- Filtering dataset')
            # plot_data_creator.filter_by_date(args.since, args.until)

        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
        plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator(interval_multiples=True))
        plt.gca().set_ylim([-10, 100])
        plt.gca().minorticks_on()

        # todo: make plot
        print('------------')
        for device, data in plot_data_creator.data.items():
            plt.plot(data.dates, data.values, label=device)

        plt.legend()
        plt.grid(which='both')

        plt.gcf().autofmt_xdate()
        plt.show()

    except Exception as e:
        print(e)


def parse_input_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--since", type=str, required=False,
                        help="Plot data newer than \'%%Y-%%m-%%d %%H:%%M:%%S\'")
    parser.add_argument("--until", type=str, required=False,
                        help="Plot data older than \'%%Y-%%m-%%d %%H:%%M:%%S\'")
    parser.add_argument("--above", type=str, required=False,
                        help="Plot values higher than")
    parser.add_argument("--below", type=str, required=False,
                        help="Plot values lower than")
    parser.add_argument('files', type=str, nargs='+',
                        help='Data sources')
    return parser.parse_args()


class PlotDataCreator:
    def __init__(self):
        self.data = dict()

    def read_csv_file(self, file):
        measured_value = None
        if 'humidity' in file:
            measured_value = 'humidity'
        elif 'temperature' in file:
            measured_value = 'temperature'
        elif 'fan' in file:
            measured_value = 'fan'
        elif 'lamp' in file:
            measured_value = 'lamp'

        with open(file) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                self._add_row(row, measured_value)

    def _add_row(self, row, measured_value):
        if len(row) != 4:
            return
        device_type = row[1]
        data_label = device_type + '-' + row[2]
        date = row[0]

        # todo: add enum as device types
        if device_type == 'sensor':
            value = float(row[3])
            if measured_value is not None:
                data_label += '-' + measured_value
        else:
            value = int(row[3])

        if data_label in self.data:
            self.data[data_label].add_record(date, value)
        else:
            self.data[data_label] = PlotData(device_type)
            self.data[data_label].add_record(date, value)

    def filter_by_date(self, since, until):
        for data_label, data in self.data.items():
            data.filter_by_date(since, until)
            self.data[data_label] = data

        for data_label, data in self.data.items():
            print(data_label, len(data.values))


class PlotData:
    def __init__(self, type):
        self.type = type
        self.dates = list()
        self.values = list()

    def add_record(self, date_string, value):
        # todo: create `filter_by_value()`
        if self.type == 'sensor':
            if len(self.values) > 0 and abs(self.values[-1] - value) / self.values[-1] > 0.1:
                return
        elif self.type == 'fan':
            value *= 10
        elif self.type == 'lamp':
            value *= 5

        date = self.date_from_string(date_string)

        if len(self.values) != 0:
            self.dates.append(date)
            self.values.append(self.values[-1])

        self.dates.append(date)
        self.values.append(value)

    def filter_by_date(self, since, until):
        if since is None and until is None:
            return

        try:
            if since is not None:
                since = self.date_from_string(since)
            if until is not None:
                until = self.date_from_string(until)
        except Exception as e:
            raise(e)

        # todo
        # self.dates = [
        #     date for date in self.dates if not self.should_remove(date, since, until)]

    def _remove_record_by_date(self, date):
        index = self.dates.index(date)
        print(index, self.values[index])
        self._remove_record_by_index(index)

    def _remove_record_by_value(self, value):
        index = self.dates.index(value)
        self._remove_record_by_index(index)

    def _remove_record_by_index(self, index):
        del self.dates[index]
        del self.values[index]

    def date_from_string(self, date):
        date_format = '%Y-%m-%d %H:%M:%S'
        return dt.datetime.strptime(date, date_format)


if __name__ == "__main__":
    main()
