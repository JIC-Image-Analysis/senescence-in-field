# Create overlay based on ground measurements

import datetime

import dtoolcore

import click

import pandas as pd

from translate_labels import image_plot_to_rack_plot


def parse_scores_file(ground_scores_file):
    senescence_scores_xls = pd.ExcelFile(ground_scores_file)
    senescence_scores = senescence_scores_xls.parse()

    def datetime_or_none(item):
        if type(item) == datetime.datetime:
            return item.strftime('2016-%m-%d')
        return None

    dates_by_rack_plot = {}
    for row_index, row in senescence_scores.iterrows():
        rack_plot = (row['Rack'], row['Plot'])
        entry = {
            'heading': datetime_or_none(row['Heading Date']),
            'leaf': datetime_or_none(row['Leaf Senescence Date']),
            'peduncle': datetime_or_none(row['Peduncle Senescence Date'])
        }
        dates_by_rack_plot[rack_plot] = entry

    return dates_by_rack_plot


def find_median_leaf_senescence_date(ground_scores_file):
    senescence_scores_xls = pd.ExcelFile(ground_scores_file)
    senescence_scores = senescence_scores_xls.parse()

    dates_only = [
        item
        for item in senescence_scores['Leaf Senescence Date']
        if type(item) == datetime.datetime
    ]

    dates_only.sort()

    mid_point = int(len(dates_only) / 2)

    return dates_only[mid_point]


def create_ground_measurements_overlay(dataset, dates_by_rack_plot):

    plot_number_overlay = dataset.get_overlay('plot_number')
    ordering_overlay = dataset.get_overlay('ordering')

    ground_measurements_overlay = {}
    for identifier in dataset.identifiers:
        try:
            n_plot = int(plot_number_overlay[identifier])
            n_image = int(ordering_overlay[identifier])
            rack, plot = image_plot_to_rack_plot(n_image, n_plot)
            entry = dates_by_rack_plot.get((rack, plot), {})
            ground_measurements_overlay[identifier] = entry
        except TypeError:
            ground_measurements_overlay[identifier] = {}

    dataset.put_overlay('ground_measurements', ground_measurements_overlay)


def create_relative_leaf_senescence_overlay(
    dataset,
    ground_scores_file,
    median_leaf_senescence_date
):
    senescence_scores_xls = pd.ExcelFile(ground_scores_file)
    senescence_scores = senescence_scores_xls.parse()

    median_leaf_senescence_date = find_median_leaf_senescence_date(
        ground_scores_file
    )

    relative_dates_by_rack_plot = {}
    for row_index, row in senescence_scores.iterrows():
        rack, plot = row['Rack'], row['Plot']
        leaf_date = row['Leaf Senescence Date']
        if type(leaf_date) == datetime.datetime:
            relative_date = (leaf_date - median_leaf_senescence_date).days
        else:
            relative_date = None
        relative_dates_by_rack_plot[(rack, plot)] = relative_date

    plot_number_overlay = dataset.get_overlay('plot_number')
    ordering_overlay = dataset.get_overlay('ordering')

    relative_leaf_senescence_overlay = {}
    for identifier in dataset.identifiers:
        try:
            n_plot = int(plot_number_overlay[identifier])
            n_image = int(ordering_overlay[identifier])
            rack, plot = image_plot_to_rack_plot(n_image, n_plot)
            relative_leaf_senescence_overlay[identifier] = \
                relative_dates_by_rack_plot.get((rack, plot), None)
        except TypeError:
            relative_leaf_senescence_overlay[identifier] = None

    dataset.put_overlay(
        'relative_leaf_senescence',
        relative_leaf_senescence_overlay
    )


@click.command()
@click.argument('dataset_uri')
@click.argument('ground_scores_file')
def main(dataset_uri, ground_scores_file):

    dataset = dtoolcore.DataSet.from_uri(dataset_uri)

    dates_by_rack_plot = parse_scores_file(ground_scores_file)

    # create_ground_measurements_overlay(dataset, dates_by_rack_plot)

    median_leaf_senescence_date = find_median_leaf_senescence_date(
        ground_scores_file
    )

    create_relative_leaf_senescence_overlay(
        dataset,
        ground_scores_file,
        median_leaf_senescence_date
    )


if __name__ == '__main__':
    main()
