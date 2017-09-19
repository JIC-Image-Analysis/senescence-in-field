"""Test indexing of plots."""

import os
import random
import argparse

from collections import defaultdict

import dtoolcore

import numpy as np

from jicbioimage.core.image import Image

from dtoolutils import (
    temp_working_dir,
    stage_outputs
)


def ensure_uri(path_or_uri):

    if ':' in path_or_uri:
        return path_or_uri
    else:
        return "disk:{}".format(path_or_uri)


def generate_plots_image(dataset, dates_to_identifiers):

    images = []
    sorted_dates = sorted(dates_to_identifiers)

    for date in sorted_dates:
        identifier = dates_to_identifiers[date]
        image_abspath = dataset.item_content_abspath(identifier)
        image = Image.from_file(image_abspath)
        images.append(image)

    output_image = join_horizontally(images)

    return output_image


def generate_plot_image_list(dataset, dates_to_identifiers):

    images = []
    sorted_dates = sorted(dates_to_identifiers)

    for date in sorted_dates:
        identifier = dates_to_identifiers[date]
        image_abspath = dataset.item_content_abspath(identifier)
        image = Image.from_file(image_abspath)
        image = generate_image_with_colour_summary(image)
        images.append(image)

    return images


def generate_tidy_data_table(dataset, working_dir):

    indexed_by_label = index_plots_by_label(dataset)

    complete_sets = [k for k, v in indexed_by_label.items() if len(v) == 5]

    # sample_labels = complete_sets[0:100]
    sample_labels = complete_sets

    output_fpath = os.path.join(working_dir, 'plot_colours.csv')
    with open(output_fpath, 'w') as fh:
        headers = ['plot', 'date', 'R', 'G', 'B']
        fh.write(','.join(headers) + '\n')
        for label in sample_labels:
            dates_to_identifiers = indexed_by_label[label]
            for date, identifier in dates_to_identifiers.items():
                image_abspath = dataset.item_content_abspath(identifier)
                image = Image.from_file(image_abspath)
                R, G, B = np.median(image, axis=[0, 1])
                items = [str(i) for i in [label, date, R, G, B]]
                fh.write(','.join(items) + '\n')

    return [('plot_colours.csv', {})]


def index_plots_by_label(dataset):
    """Return dictionary of dictionaries such that all plots are indexed by
    a unique label, and then by date, so any individual plot is:

    index_by_label[label][date]."""

    date_overlay = dataset.get_overlay('date')
    ordering_overlay = dataset.get_overlay('ordering')
    plot_number_overlay = dataset.get_overlay('plot_number')

    def generate_plot_label(identifier):
        return "{}_{}".format(
            ordering_overlay[identifier],
            plot_number_overlay[identifier]
        )

    indexed_by_label = defaultdict(dict)
    for i in dataset.identifiers:
        label = generate_plot_label(i)
        date = date_overlay[i]
        indexed_by_label[label][date] = i

    return indexed_by_label


def arrange_in_grid(image_series):

    n_rows = len(image_series[0])
    n_cols = len(image_series)

    x_dims = []
    y_dims = []
    for row in image_series:
        for image in row:
            x_dim, y_dim, _ = image.shape
            x_dims.append(x_dim)
            y_dims.append(y_dim)

    xmax = max(x_dims)
    ymax = max(y_dims)

    output_x_dim = max(x_dims) * n_rows
    output_y_dim = max(y_dims) * n_cols

    output_image = np.zeros((output_x_dim, output_y_dim, 3), dtype=np.uint8)

    y_offset = 0
    for col in image_series:
        x_offset = 0
        for image in col:
            i_xdim, i_ydim, _ = image.shape
            output_image[x_offset:x_offset+i_xdim, y_offset:i_ydim+y_offset] = image
            x_offset = x_offset + xmax
        y_offset = y_offset + ymax

    return output_image.view(Image)


def explore_plot_indexing(dataset, working_dir):

    indexed_by_label = index_plots_by_label(dataset)

    complete_sets = [k for k, v in indexed_by_label.items() if len(v) == 5]

    # sample_labels = random.sample(complete_sets, 10)
    sample_labels = complete_sets[0:20]

    time_progression_image_series = [
        generate_plot_image_list(dataset, indexed_by_label[l])
        for l in sample_labels
    ]

    joined_image = arrange_in_grid(time_progression_image_series)

    output_fpath = os.path.join(working_dir, 'joined.png')
    with open(output_fpath, 'wb') as fh:
        fh.write(joined_image.png())

    return [('joined.png', {})]


def generate_image_with_colour_summary(image):
    """Return image containing both original image and solid block colour
    summary below it."""

    xdim, ydim, _ = image.shape

    output_image = np.zeros((xdim * 2, ydim, 3), dtype=np.uint8)

    output_image[0:xdim, 0:ydim] = image
    output_image[xdim:2*xdim,0:ydim,:] = np.median(image, axis=[0, 1])

    return output_image


def test_plot_colour_summary(dataset, working_dir):

    identifiers = dataset.identifiers

    identifier = identifiers[2004]

    plot_image = Image.from_file(dataset.item_content_abspath(identifier))
    output_image = generate_image_with_colour_summary(plot_image)

    output_fpath = os.path.join(working_dir, 'colour.png')
    with open(output_fpath, 'wb') as fh:
        fh.write(output_image.view(Image).png())

    return [('colour.png', {})]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset-uri')
    parser.add_argument('--output-uri')

    args = parser.parse_args()

    dataset_uri = ensure_uri(args.dataset_uri)
    output_uri = ensure_uri(args.output_uri)
    dataset = dtoolcore.DataSet.from_uri(dataset_uri)
    output_dataset = dtoolcore.ProtoDataSet.from_uri(output_uri)

    with temp_working_dir() as working_dir:
        # outputs = explore_plot_indexing(dataset, working_dir)
        outputs = generate_tidy_data_table(dataset, working_dir)
        # outputs = test_plot_colour_summary(dataset, working_dir)
        stage_outputs(
            outputs,
            working_dir,
            dataset,
            output_dataset,
            [],
            None
        )


if __name__ == '__main__':
    main()
