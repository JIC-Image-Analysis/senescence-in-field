"""I've run out of good names."""

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

from image_utils import join_horizontally, join_vertically

def ensure_uri(path_or_uri):

    if ':' in path_or_uri:
        return path_or_uri
    else:
        return "disk:{}".format(path_or_uri)


def make_lovely_plots(dataset, working_dir):

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

    young_plots = ['55_24', '50_14', '54_18', '16_17', '47_14']
    old_plots = ['8_6', '49_6', '29_17', '9_6', '21_1']

    def labels_to_joined_image(labels):
        images = []
        for plot_label in labels:
            image_fpath = dataset.item_content_abspath(label_to_id[plot_label])
            image = Image.from_file(image_fpath)
            images.append(image)

        return join_horizontally(images)

    young = labels_to_joined_image(young_plots)
    old = labels_to_joined_image(old_plots)

    result = join_vertically([young, old])

    output_fname = os.path.join(working_dir, 'extremal_plot_images.png')

    with open(output_fname, 'wb') as fh:
        fh.write(result.png())

    return [('extremal_plot_images.png', {})]


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
        # outputs = generate_tidy_data_table(dataset, working_dir)
        # outputs = test_plot_colour_summary(dataset, working_dir)
        outputs = make_lovely_plots(dataset, working_dir)
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
