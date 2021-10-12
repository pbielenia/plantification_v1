#!/usr/bin/python3
import argparse
import csv
import matplotlib.pyplot as plt


def main():
    try:
        args = parse_input_args()
        measurements = get_measurements(args.file)
        values = extract_values(measurements)
        filtered_values = remove_peaks(
            values, args.bottom_filter, args.upper_filter)

        if args.output:
            export_values(filtered_values, args.output)

        if args.plot:
            plot_values(filtered_values)

    except Exception as e:
        print('-- Something went wrong: {}'.format(e))


def parse_input_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", required=True,
                        help="Source file")
    parser.add_argument("-b", "--bottom-filter", type=int, required=True,
                        help="Throw values below")
    parser.add_argument("-u", "--upper-filter", type=int, required=True,
                        help="Throw values above")
    parser.add_argument("-o", "--output", help="Save results to")
    parser.add_argument("-p", "--plot", action='store_true',
                        help="Display plot")
    return parser.parse_args()


def get_measurements(file):
    print('-- Reading data from file \"{}\".'.format(file))
    measurements = list()
    with open(file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            measurements.append(row)
    print('-- Read {} lines.'.format(len(measurements)))
    return measurements


def extract_values(measurements):
    values = list()
    for measurement in measurements:
        if len(measurement) == 4:
            values.append(float(measurement[3]))
    print('-- Extracted {} values.'.format(len(values)))
    return values


def remove_peaks(values, bottom_filter, upper_filter):
    filtered_values = list()
    number_of_peaks = 0
    for value in values:
        if value > bottom_filter and value < upper_filter:
            filtered_values.append(value)
        else:
            number_of_peaks += 1
    print('-- Threw out {} peaks'.format(number_of_peaks))
    return filtered_values


def export_values(values, output_file):
    if output_file is None:
        output_file = 'output.txt'

    file = open(output_file, 'w')
    for value in values:
        file.write('{}\n'.format(value))
    file.close()
    print('-- Output written to file {}.'.format(output_file))


def plot_values(values):
    print('-- Creating a plot...')
    plt.plot(values)
    plt.grid()
    plt.show()


if __name__ == "__main__":
    main()
