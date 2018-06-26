# Generate overlay corresponding to 2nd PCA component
# which serves as a proxy for senescence

import csv

from collections import defaultdict

import dtoolcore

import click

import numpy as np


def calc_pca_components(all_entries):

    rgb_matrix = np.transpose(np.array(
        [
            map(float, [entry['R'], entry['G'], entry['B']])
            for entry in all_entries
        ]
    ))

    cov = np.cov(rgb_matrix)

    evalues, evectors = np.linalg.eig(cov)

    return evectors.T


def calc_senescence(entry, pca_rotation):

    c_R = pca_rotation[0] * float(entry['R'])
    c_G = pca_rotation[1] * float(entry['G'])
    c_B = pca_rotation[2] * float(entry['B'])

    return c_R + c_G + c_B


def find_senescence_values_by_plot_and_date(results):

    pca_components = calc_pca_components(results)
    pca_component_2 = pca_components[1]

    by_plot_then_date = defaultdict(dict)
    for entry in results:
        senescence = calc_senescence(entry, pca_component_2)
        by_plot_then_date[entry['plot']][entry['date']] = senescence

    return by_plot_then_date


def generate_pca_overlay(dataset, results):

    senescence_values = find_senescence_values_by_plot_and_date(results)

    plot_number_overlay = dataset.get_overlay('plot_number')
    ordering_overlay = dataset.get_overlay('ordering')
    date_overlay = dataset.get_overlay('date')

    pca_overlay = {}

    for identifier in dataset.identifiers:
        label = "{}_{}".format(
            plot_number_overlay[identifier],
            ordering_overlay[identifier]
        )
        date = date_overlay[identifier]

        try:
            senescence = senescence_values[label][date]
        except KeyError:
            senescence = None

        pca_overlay[identifier] = senescence

    dataset.put_overlay('pca_component_2', pca_overlay)


def load_output_csv_data(results_file):

    with open(results_file, 'r') as fh:
        reader = csv.DictReader(fh)

        all_entries = [row for row in reader]

    return all_entries


@click.command()
@click.argument('dataset_uri')
@click.argument('results_csv_file')
def main(dataset_uri, results_csv_file):
    dataset = dtoolcore.DataSet.from_uri(dataset_uri)

    results = load_output_csv_data(results_csv_file)

    generate_pca_overlay(dataset, results)


if __name__ == '__main__':
    main()
