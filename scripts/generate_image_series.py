# Draw image time series for one or more plots

from jicbioimage.core.image import Image

import dtoolcore

import click

from translate_labels import rack_plot_to_image_plot
from image_utils import join_horizontally, join_vertically


def identifiers_where_match_is_true(dataset, match_function):

    return [i for i in dataset.identifiers if match_function(i)]


def generate_image_series_for_plot(rack, plot):

    n_image, n_plot = rack_plot_to_image_plot(rack, plot)

    # n_image, n_plot = 55, 24

    print "{}_{}".format(n_image, n_plot)

    dataset_uri = 'file:/Users/hartleym/data_intermediate/separate_plots'
    dataset = dtoolcore.DataSet.from_uri(dataset_uri)

    plot_number_overlay = dataset.get_overlay('plot_number')
    ordering_overlay = dataset.get_overlay('ordering')
    date_overlay = dataset.get_overlay('date')

    def is_match(i):
        try:
            ordering_as_int = int(ordering_overlay[i])
        except TypeError:
            return False

        if ordering_as_int != n_image:
            return False

        if int(plot_number_overlay[i]) != n_plot:
            return False

        return True

    identifiers = identifiers_where_match_is_true(dataset, is_match)

    def sort_identifiers_by_date(identifiers):

        dates_and_identifiers = [(date_overlay[i], i) for i in identifiers]
        sorted_dates_and_identifiers = sorted(dates_and_identifiers)

        _, sorted_identifiers = zip(*sorted_dates_and_identifiers)

        return(sorted_identifiers)

    sorted_identifiers = sort_identifiers_by_date(identifiers)

    def identifiers_to_joined_image(identifiers):
        images = []
        for identifier in identifiers:
            image_fpath = dataset.item_content_abspath(identifier)
            image = Image.from_file(image_fpath)
            images.append(image)

        return join_horizontally(images)

    result = identifiers_to_joined_image(sorted_identifiers)
    output_fname = 'example_from_tobin.png'

    with open(output_fname, 'wb') as fh:
        fh.write(result.png())


@click.command()
def main():

    # Early leaf senescence
    # generate_image_series_for_plot(3, 16)
    # generate_image_series_for_plot(7, 9)
    # generate_image_series_for_plot(9, 1)

    # Late leaf senescence
    generate_image_series_for_plot(7, 15)
if __name__ == '__main__':
    main()
