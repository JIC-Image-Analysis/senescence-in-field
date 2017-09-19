"""Tile images."""

import os
import random
import argparse

from collections import defaultdict

import dtoolcore

import numpy as np

from jicbioimage.core.image import Image

from skimage.transform import downscale_local_mean

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


def tile_plots(dataset, working_dir):

    is_jpeg_overlay = dataset.get_overlay("is_jpeg")
    date_overlay = dataset.get_overlay("date")
    ordering_overlay = dataset.get_overlay("ordering")

    dates = set(date_overlay.values())

    fnames = []
    dates = ['2016-06-28']

    # print [date_overlay[identifier] for identifier in dataset.identifiers]

    for date in dates:

        selected = {}
        for identifier in dataset.identifiers:
            if is_jpeg_overlay[identifier] and date_overlay[identifier] == date:
                try:
                    selected[ordering_overlay[identifier]] = identifier
                except TypeError:
                    pass

        print(selected.keys())

        def generate_column(numbers):
            images = []
            for i in numbers:
                i = selected[i]
                image_fpath = dataset.item_content_abspath(i)
                images.append(
                    downscale_local_mean(Image.from_file(image_fpath), (5, 5, 1))
                )

            column = join_horizontally(images)

            return column

        columns = []
        for o in range(12):
            numbers = range(59-o, 10-o, -12)
            columns.append(generate_column(numbers))

        tiled = join_vertically(columns)

        fname = 'tiled-{}.png'.format(date)
        output_fpath = os.path.join(working_dir, fname)
        with open(output_fpath, 'wb') as fh:
            fh.write(tiled.png())

        fnames.append((fname, {}))

    return fnames


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
        outputs = tile_plots(dataset, working_dir)
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
