"""Select interesting plots."""

import csv

import numpy as np

import click

import dtoolcore


def calc_senescence(entry, pca_rotation):

    c_R = pca_rotation[0]
    c_G = pca_rotation[1]
    c_B = pca_rotation[2]

    return c_R * float(entry['R']) + c_G * float(entry['G']) + c_B * float(entry['B'])


def calc_all_senescence(all_entries, pca_rotation):

    for entry in all_entries:
        entry['senescence'] = calc_senescence(entry, pca_rotation)


def load_data(results_file):

    with open(results_file, 'r') as fh:
        reader = csv.DictReader(fh)

        all_entries = [row for row in reader]



    return all_entries


def select_by_date_and_sort(all_entries, date):

    selected = [
        (entry['senescence'], entry['plot'])
        for entry in all_entries
        if entry['date'] == date
    ]

    selected.sort()

    return selected


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


@click.command()
@click.argument('results_file')
def main(results_file):

    all_entries = load_data(results_file)

    # print('\n'.join(str(e) for e in [
    #     entry
    #     for entry in all_entries
    #     if entry['plot'] == '24_11'
    #     ]))


    pca_rotation = calc_pca_components(all_entries)[1]
    calc_all_senescence(all_entries, pca_rotation)

    selected_22 = select_by_date_and_sort(all_entries, '2016-07-22')
    selected_15 = select_by_date_and_sort(all_entries, '2016-07-15')

    extreme_22 = set(s[1] for s in selected_22[0:50])
    extreme_15 = set(s[1] for s in selected_15[0:50])

    print extreme_22 & extreme_15

    # print selected[0:10]
    # print selected[-10:-1]

    # label1 = selected[11][1]
    # label2 = selected[-11][1]


    dataset_uri = 'disk:/Users/hartleym/data_intermediate/separate_plots'
    dataset = dtoolcore.DataSet.from_uri(dataset_uri)

    date_overlay = dataset.get_overlay('date')
    ordering_overlay = dataset.get_overlay('ordering')
    plot_number_overlay = dataset.get_overlay('plot_number')

    def generate_plot_label(identifier):
        return "{}_{}".format(
            ordering_overlay[identifier],
            plot_number_overlay[identifier]
        )

    date = '2016-07-15'
    label_to_id = {
        generate_plot_label(i): i for i in dataset.identifiers
        if date_overlay[i] == date
    }


    # ids_of_interest = [label_to_id[s[1]] for s in selected[10:20]]

    # print(ids_of_interest)

    # print(dataset.item_content_abspath(label_to_id[label1]))
    # print(dataset.item_content_abspath(label_to_id[label2]))

    young_plots = ['55_24', '50_14', '54_18', '16_9', '47_14']
    old_plots = ['8_6', '49_6', '29_17', '9_6', '21_1']

    for label in old_plots:
        print(dataset.item_content_abspath(label_to_id[label]))

if __name__ == '__main__':
    main()
