
import os
import argparse

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

from dtoolcore import DataSet

from utils import (
    red_channel,
    green_channel,
    difference,
    fill_small_holes,
)

from segment import filter_sides, filter_touching_border

from jicgeometry import Point2D


def find_approx_plot_locs(dataset, identifier):
    corner_coords = dataset.access_overlays()["coords"][identifier]

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
def segment(image, seeds=None):
    """Return field plots."""
    green = green_channel(image)

    image = sklocal(green)
    image = skmean(image)

    mask = threshold_otsu(image)
    mask = remove_small_objects(mask, min_size=1000)
    mask = fill_small_holes(mask, min_size=100)

    if seeds is None:
        seeds = erode_binary(mask, selem=disk(10))
        seeds = remove_small_objects(seeds, min_size=100)
        seeds = connected_components(seeds, background=0)

    return watershed_with_seeds(image, seeds=seeds, mask=mask)


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


def generate_output_filename(dataset, identifier, output_path, suffix=""):

    output_basename = os.path.basename(
        dataset.abspath_from_identifier(identifier)
    )

    name, ext = os.path.splitext(output_basename)

    output_filename = name + suffix + ext

    full_output_filename = os.path.join(output_path, output_filename)

    return full_output_filename


def process_single_identifier(dataset, identifier, output_path):

    print("Processing {}".format(identifier))

    image = Image.from_file(dataset.abspath_from_identifier(identifier))

    seeds = generate_seed_image(image, dataset, identifier)

    segmentation = segment(image, seeds)
    segmentation = filter_sides(segmentation)
    segmentation = filter_touching_border(segmentation)

    output_filename = generate_output_filename(
        dataset,
        identifier,
        output_path,
        '-segmented'
    )
    with open(output_filename, 'wb') as fh:
        fh.write(segmentation.png())


def identifiers_where_overlay_is_true(dataset, overlay_name):

    overlays = dataset.access_overlays()

    selected = [identifier
                for identifier in dataset.identifiers
                if overlays[overlay_name][identifier]]

    return selected


def identifiers_where_overlay_matches_value(dataset, overlay_name, value):

    overlays = dataset.access_overlays()

    selected = [identifier
                for identifier in dataset.identifiers
                if overlays[overlay_name][identifier] == value]

    return selected


def explore_dataset(dataset, output_path, n=1):
    ids_of_interest = identifiers_where_overlay_matches_value(
        dataset, 'ordering', 0
    )

    print(ids_of_interest)

    for identifier in ids_of_interest:
        process_single_identifier(dataset, identifier, output_path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('dataset_path', help='Path to dataset')
    parser.add_argument('output_path', help='Output directory')

    args = parser.parse_args()

    AutoName.directory = args.output_path

    dataset = DataSet.from_path(args.dataset_path)

    explore_dataset(dataset, args.output_path, n=1)


if __name__ == '__main__':
    main()
