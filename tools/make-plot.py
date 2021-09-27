import argparse
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime as dt
import csv


def main():
    # todo: get all files from the given directory and pass them to the plot_data_creator

    args = parse_input_args()
    plot_data_creator = PlotDataCreator()

    for file in args.files:
        plot_data_creator.read_csv_file(file)
        # plot_data_creator.filter_by_date(args.since, args.until)

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
    plt.gca().xaxis.set_major_locator(mdates.HourLocator())

    for device, data in plot_data_creator.data.items():
        plt.plot(data.dates, data.values)

    # plt.plot(fan3_data.dates, fan3_data.values)
    plt.gcf().autofmt_xdate()

    plt.show()


def parse_input_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--since", type=int, required=False,
                        help="Plot data newer than")
    parser.add_argument("--until", type=int, required=False,
                        help="Plot data older than")
    parser.add_argument('files', type=str, nargs='+',
                        help='Data sources')
    # parser.add_argument("-o", "--output", help="Save results to")
    # parser.add_argument("-p", "--plot", action='store_true',
    #                     help="Display plot")
    return parser.parse_args()


class PlotDataCreator:
    def __init__(self):
        self.data = dict()

    def read_csv_file(self, file):
        with open(file) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                self._add_row(row)

    def _add_row(self, row):
        if len(row) != 4:
            return
        device_name = row[1] + '-' + row[2]
        date = row[0]
        value = row[3]

        if device_name in self.data:
            self.data[device_name].add_record(date, value)
        else:
            self.data[device_name] = PlotData()
            self.data[device_name].add_record(date, value)

    # def filter_by_date(self, since, until):
    #     for device_name, data in self.data.items():
    #         data.filter_by_date(since, until)


class PlotData:
    def __init__(self):
        self.dates = list()
        self.values = list()

    def add_record(self, date_string, value):
        date = self.date_from_string(date_string)

        if len(self.values) != 0:
            self.dates.append(date)
            self.values.append(self.values[-1])

        self.dates.append(date)
        self.values.append(value)

    # def filter_by_date(self, since, until):
    #     print('since = {}, until = {}'.format(since, until))
    #     for date in self.dates:
    #         print('\t' + str(date))
    #         if date < since:
    #             print('\t\tTrue')
    #         else:
    #             print('\t\tFalse')

    #     exit(0)

    def date_from_string(self, date):
        date_format = '%Y-%m-%d %H:%M:%S'
        return dt.datetime.strptime(date, date_format)


if __name__ == "__main__":
    main()
