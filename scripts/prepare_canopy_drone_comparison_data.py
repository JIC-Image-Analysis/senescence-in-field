# C

import csv
from datetime import datetime
from collections import defaultdict

import click

import numpy as np
import pandas as pd

from scipy.interpolate import interp1d

from translate_labels import image_plot_to_rack_plot


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


def load_data(results_file):

    with open(results_file, 'r') as fh:
        reader = csv.DictReader(fh)

        all_entries = [row for row in reader]

    return all_entries


def calc_senescence(entry, pca_rotation):

    c_R = pca_rotation[0]
    c_G = pca_rotation[1]
    c_B = pca_rotation[2]

    return c_R * float(entry['R']) + c_G * float(entry['G']) + c_B * float(entry['B'])


def estimate_senescence_date(senescence_by_date, s_thresh=0):

    base_datetime = datetime(2016, 6, 28)

    def get_days_since_base(date_string):
        time_delta = datetime.strptime(date_string, "%Y-%m-%d") - base_datetime
        return time_delta.days

    def unpack_and_get_days((date_string, s)):
        return get_days_since_base(date_string), s

    days_and_s = map(unpack_and_get_days, senescence_by_date.items())

    sorted_days_and_s = sorted(days_and_s)

    x, y = zip(*sorted_days_and_s)

    interpolator = interp1d(y, x, fill_value='extrapolate')

    return interpolator(s_thresh)


def parse_results_file(results_file):

    all_entries = load_data(results_file)

    pca_component_2 = calc_pca_components(all_entries)[1]

    senescence_by_plot = defaultdict(dict)

    for entry in all_entries:
        date = entry['date']
        plot = entry['plot']

        senescence_score = calc_senescence(entry, pca_component_2)

        senescence_by_plot[plot][date] = senescence_score

    for k, v in senescence_by_plot.items():
        image, iplot = map(int, k.split('_'))
        rack, plot = image_plot_to_rack_plot(image, iplot)
        print(rack, plot, estimate_senescence_date(v, -10))


def parse_scores_file(ground_scores_file):
    senescence_scores_xls = pd.ExcelFile(ground_scores_file)
    senescence_scores = senescence_scores_xls.parse()

    # base_datetime = senescence_scores['Leaf Senescence Date'][0]
    base_datetime = datetime.datetime(2018, 6, 28)

    def clean_item(item):
        if type(item) == datetime:
            return item
        else:
            return base_datetime

    cleaned = map(clean_item, senescence_scores['Leaf Senescence Date'])

    print(len(cleaned))
    print(len(senescence_scores['Plot']))


@click.command()
@click.argument('results_file')
@click.argument('ground_scores_file')
def main(results_file, ground_scores_file):

    # parse_scores_file(ground_scores_file)

    parse_results_file(results_file)


if __name__ == '__main__':
    main()
