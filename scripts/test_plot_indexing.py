"""Test indexing of plots."""

import argparse

from collections import defaultdict

import dtoolcore

import numpy as np

from jicbioimage.core.image import Image


def ensure_uri(path_or_uri):

    if ':' in path_or_uri:
        return path_or_uri
    else:
        return "disk:{}".format(path_or_uri)


def generate_plots_image(dataset, dates_to_identifiers):

    images = []
    for date, identifier in dates_to_identifiers.items():
        image_abspath = dataset.item_content_abspath(identifier)
        image = Image.from_file(image_abspath)
        images.append(image)

    x_dims = [image.shape[0] for image in images]
    y_dims = [image.shape[1] for image in images]

    x_dim = max(x_dims)
    y_dim = 5 * max(y_dims)

    output_image = np.zeros((x_dim, y_dim, 3), dtype=np.uint8)

    offset = 0
    for n, image in enumerate(images):
        # offset = y_dim * n
        i_xdim, i_ydim, _ = image.shape
        # print("{}:{}".format(offset, i_ydim+offset))
        output_image[0:i_xdim, offset:i_ydim+offset] = image
        offset = offset + i_ydim

    with open('/output/test.png', 'wb') as fh:
        fh.write(output_image.view(Image).png())


def explore_plot_indexing(dataset):

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

    complete_sets = [k for k, v in indexed_by_label.items() if len(v) == 5]

    test_label = complete_sets[0]

    generate_plots_image(dataset, indexed_by_label[test_label])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset-uri')
    parser.add_argument('--output-uri')

    args = parser.parse_args()

    dataset_uri = ensure_uri(args.dataset_uri)
    output_uri = ensure_uri(args.output_uri)
    dataset = dtoolcore.DataSet.from_uri(dataset_uri)
    output_dataset = dtoolcore.ProtoDataSet.from_uri(output_uri)

    explore_plot_indexing(dataset)


if __name__ == '__main__':
    main()
