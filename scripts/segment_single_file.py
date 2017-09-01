
import os
import shutil
import argparse
import tempfile

from contextlib import contextmanager

import numpy as np
from skimage.morphology import disk

from jicbioimage.core.io import AutoName, AutoWrite

from jicbioimage.core.image import Image
from jicbioimage.core.transform import transformation
from jicbioimage.transform import (
    threshold_otsu,
    remove_small_objects,
    erode_binary,
)
from jicbioimage.segment import connected_components, watershed_with_seeds

from dtoolcore import DataSet, ProtoDataSet

from utils import (
    red_channel,
    green_channel,
    difference,
    fill_small_holes,
)

from segment import filter_sides, filter_touching_border

from jicgeometry import Point2D

TMPDIR_PREFIX = '/tmp'


@contextmanager
def temp_working_dir():
    working_dir = tempfile.mkdtemp(prefix=TMPDIR_PREFIX)

    try:
        yield working_dir
    finally:
        shutil.rmtree(working_dir)


def find_approx_plot_locs(dataset, identifier):
    corner_coords = dataset.get_overlay("coords")[identifier]

    def coords_to_point2d(coords):
        x = float(coords['x'])
        y = float(coords['y'])

        return Point2D(x, y)

    top_left = coords_to_point2d(corner_coords['topLeft'])
    bottom_left = coords_to_point2d(corner_coords['bottomLeft'])
    top_right = coords_to_point2d(corner_coords['topRight'])

    vdiff = bottom_left - top_left
    hdiff = top_right - top_left

    plot_locs = []

    for hmult in np.linspace(0, 1, 6):
        for vmult in np.linspace(0, 1, 5):
            plot_locs.append(top_left + hdiff * hmult + vdiff * vmult)

    return plot_locs


def normalise_array(array):

    a_min = array.min()
    a_max = array.max()

    return (array - a_min) / (a_max - a_min)


def force_to_uint8(array):

    normalised = normalise_array(array)
    scaled = normalised * 255

    return scaled.astype(np.uint8)


@transformation
def sklocal(image):

    from skimage.filters.rank import entropy

    le = entropy(image, disk(5))

    return force_to_uint8(le)


@transformation
def skmean(image):

    from skimage.filters.rank import mean

    mean_filtered = mean(image, disk(30))

    print mean_filtered.min(), mean_filtered.max()

    return mean_filtered


@transformation
def distance_transform(image):
    from skimage.morphology import medial_axis

    _, dist = medial_axis(image, return_distance=True)

    return dist


@transformation
def segment(image, seeds=None):
    """Return field plots."""
    green = green_channel(image)

    image = sklocal(green)
    image = skmean(image)

    mask = threshold_otsu(image)
    mask = remove_small_objects(mask, min_size=1000)
    mask = fill_small_holes(mask, min_size=100)
    dist = distance_transform(mask)

    if seeds is None:
        seeds = erode_binary(mask, selem=disk(10))
        seeds = remove_small_objects(seeds, min_size=100)
        seeds = connected_components(seeds, background=0)

    return watershed_with_seeds(image, seeds=seeds, mask=mask)


@transformation
def filter_by_size(plots):
    """Remove plots the size of which lies outside particular min and max plot
    sizes."""

    # params = Parameters()

    identifiers = plots.identifiers

    # TODO - set relative to median?
    min_plot_size = 20000
    max_plot_size = 120000

    for identifier in identifiers:
        region = plots.region_by_identifier(identifier)
        size = region.area
        if (size < min_plot_size) or (size > max_plot_size):
            plots.remove_region(identifier)

    return plots


def generate_seed_image(image, dataset, identifier):

    seeds_as_list = find_approx_plot_locs(dataset, identifier)

    xdim, ydim, _ = image.shape

    seeds = np.zeros((xdim, ydim), dtype=np.uint8)
    for n, seed in enumerate(seeds_as_list):
        xfrac, yfrac = seed
        x = int(yfrac * xdim)
        y = int(xfrac * ydim)

        seeds[x, y] = n

    return seeds


def save_segmented_image_as_rgb(segmented_image, filename):

    segmentation_as_rgb = segmented_image.unique_color_image

    with open(filename, 'wb') as f:
        f.write(segmentation_as_rgb.png())


def segment_single_identifier(dataset, identifier, working_dir):

    fpath = dataset.item_content_abspath(identifier)

    image = Image.from_file(fpath)

    seeds = generate_seed_image(image, dataset, identifier)

    segmentation = segment(image, seeds)
    segmentation = filter_sides(segmentation)
    segmentation = filter_touching_border(segmentation)

    output_filename = os.path.join(working_dir, 'segmentation.png')
    save_segmented_image_as_rgb(segmentation, output_filename)

    false_colour_filename = os.path.join(working_dir, 'false_color.png')
    with open(false_colour_filename, 'wb') as fh:
        fh.write(segmentation.png())

    segmentation_output = ('segmentation.png', {'type': 'segmentation'})
    false_colour_output = ('false_color.png', {'type': 'false_color'})

    return [segmentation_output, false_colour_output]


def stage_outputs(
    outputs,
    working_dir,
    dataset,
    output_dataset,
    overlays_to_copy,
    identifier
):

    for filename, metadata in outputs:
        src_abspath = os.path.join(working_dir, filename)
        useful_name = dataset.get_overlay('useful_name')[identifier]
        relpath = os.path.join(useful_name, filename)
        output_dataset.put_item(src_abspath, relpath)

        # Add 'from' overlay
        output_dataset.add_item_metadata(relpath, 'from', identifier)

        # Copy overlays
        for overlay_name in overlays_to_copy:
            value = dataset.get_overlay(overlay_name)[identifier]
            output_dataset.add_item_metadata(relpath, overlay_name, value)

        # Add extra metadata
        for k, v in metadata.items():
            output_dataset.add_item_metadata(relpath, k, v)


class SmartTool(object):

    def __init__(self):
        parser = argparse.ArgumentParser()

        parser.add_argument(
            '-d',
            '--dataset-uri',
            help='URI of input dataset'
        )
        parser.add_argument(
            '-i',
            '--identifier',
            help='Identifier to process'
        )
        parser.add_argument(
            '-o',
            '--output-dataset-uri',
            help='URI of output dataset'
        )

        args = parser.parse_args()

        self.input_dataset = DataSet.from_uri(args.dataset_uri)
        self.output_dataset = ProtoDataSet.from_uri(args.output_dataset_uri)

        self.identifier = args.identifier

    def stage_outputs(self, working_directory):
        for filename in self.outputs:

            useful_name = self.input_dataset.access_overlay(
                'useful_name'
            )[self.identifier]

            fpath = os.path.join(working_directory, filename)
            relpath = os.path.join(useful_name, filename)
            out_id = self.output_dataset.put_item(fpath, relpath)
            self.output_dataset.add_item_metadata(
                out_id,
                'from',
                "{}/{}".format(self.input_dataset.uuid, self.identifier)
                )

    def run(self):
        input_file_path = self.input_dataset.item_contents_abspath(
            self.identifier
        )

        with temp_working_dir() as working_directory:
            runner = DockerAssist(self.container, self.command_string)
            runner.add_volume_mount(input_file_path, '/input1')
            runner.add_volume_mount(working_directory, '/output')

            runner.run()

            self.stage_outputs(working_directory)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset-uri', help='Dataset URI')
    parser.add_argument('--identifier', help='Identifier (hash) to process')
    parser.add_argument(
        '--output-uri',
        help='Output dataset uri'
    )

    args = parser.parse_args()

    dataset = DataSet.from_uri(args.dataset_uri)
    output_dataset = ProtoDataSet.from_uri(args.output_uri)

    with temp_working_dir() as working_dir:

        outputs = segment_single_identifier(
            dataset,
            args.identifier,
            working_dir
        )

        overlays_to_copy = ['coords', 'ordering', 'useful_name']

        stage_outputs(
            outputs,
            working_dir,
            dataset,
            output_dataset,
            overlays_to_copy,
            args.identifier
        )


if __name__ == '__main__':
    main()
