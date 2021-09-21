import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime as dt
import csv


class PlotDataCreator:
    def __init__(self):
        self.data = dict()

    def read_csv_file(self, file):
        with open('measures/fan.csv.2021-09-20') as csv_file:
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


class PlotData:
    def __init__(self):
        self.dates = list()
        self.values = list()

    def add_record(self, date, value):
        date_format = '%Y-%m-%d %H:%M:%S'
        formatted_date = dt.datetime.strptime(date, date_format)

        if len(self.values) != 0:
            self.dates.append(formatted_date)
            self.values.append(self.values[-1])

        self.dates.append(formatted_date)
        self.values.append(int(value))


def main():
    # todo: get all files from the given directory and pass them to the plot_data_creator

    plot_data_creator = PlotDataCreator()
    plot_data_creator.read_csv_file('measures/fan.csv.2021-09-20')

    # todo: iterate over data adding it to the plot
    fan_data = plot_data_creator.data['fan-1']

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
    plt.gca().xaxis.set_major_locator(mdates.HourLocator())
    plt.plot(fan_data.dates, fan_data.values)
    plt.gcf().autofmt_xdate()

    plt.show()


if __name__ == "__main__":
    main()
