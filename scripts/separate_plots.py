"""Separate individual plots."""

import os
import argparse

import numpy as np

from scipy.misc import imsave

from jicbioimage.core.image import Image
from jicbioimage.segment import SegmentedImage

from dtoolcore import DataSet, ProtoDataSet

from jicgeometry import Point2D

from dtoolutils import temp_working_dir


def load_segmentation_from_rgb_image(filename):

    rgb_image = Image.from_file(filename)

    ydim, xdim, _ = rgb_image.shape

    segmentation = np.zeros((ydim, xdim), dtype=np.uint32)

    segmentation += rgb_image[:, :, 2]
    segmentation += rgb_image[:, :, 1].astype(np.uint32) * 256
    segmentation += rgb_image[:, :, 0].astype(np.uint32) * 256 * 256

    return segmentation.view(SegmentedImage)


def generate_region_image(original_image, segmentation, identifier):
    """Generate image of section of original image represented by the region
    of the segmentation with the given identifier."""

    region = segmentation.region_by_identifier(identifier)

    region_rgb = np.dstack([region] * 3)
    masked_image = region_rgb * original_image

    rmin, rmax = min(region.index_arrays[0]), max(region.index_arrays[0])
    cmin, cmax = min(region.index_arrays[1]), max(region.index_arrays[1])

    image_section = masked_image[rmin:rmax, cmin:cmax]

    return image_section


def find_approx_plot_locs(dataset, identifier):
    """Return array of approximate plot locations based on the corner locations
    identified through clicking with a tagger.

    These are calculated by dividing the space between the corers into a grid
    based on the known numbers of plots (6 horizontal, 5 vertical).

    Points are returned in normalised coordinates."""

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


def image_coords_to_rel_coords(image, point):

    ydim, xdim = image.shape
    y_abs, x_abs = point

    x_rel = float(x_abs) / xdim
    y_rel = float(y_abs) / ydim

    return Point2D(x_rel, y_rel)


def generate_segmentation_identifier_to_label_map(
    approx_plot_locs,
    segmentation
):
    """Generate dictionary mapping segmentation identifiers to numberical id
    of plot in field. This id should be consistent across images."""

    loc_labels = {l: str(n) for n, l in enumerate(approx_plot_locs)}

    def closest_loc_label(p):
        dists = [(p.distance(l), l) for l in approx_plot_locs]

        dists.sort()

        return loc_labels[dists[0][1]]

    sid_to_label = {}

    for sid in segmentation.identifiers:
        c = segmentation.region_by_identifier(sid).centroid
        c_rel = image_coords_to_rel_coords(segmentation, c)
        sid_to_label[sid] = closest_loc_label(c_rel)

    return sid_to_label


def separate_plots(dataset, identifier, resource_dataset, working_dir):

    fpath = dataset.item_content_abspath(identifier)
    segmentation = load_segmentation_from_rgb_image(fpath)

    original_id = dataset.get_overlay('from')[identifier]
    original_fpath = resource_dataset.item_content_abspath(original_id)
    original_image = Image.from_file(original_fpath)

    approx_plot_locs = find_approx_plot_locs(dataset, identifier)

    sid_to_label = generate_segmentation_identifier_to_label_map(
        approx_plot_locs,
        segmentation
    )

    for identifier in segmentation.identifiers:

        image_section = generate_region_image(
            original_image,
            segmentation,
            identifier
        )

        output_fpath = os.path.join(
            working_dir,
            'region_{}.png'.format(sid_to_label[identifier])
        )

        imsave(output_fpath, image_section)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset-uri')
    parser.add_argument('--resource-uri')
    parser.add_argument('--identifier')
    parser.add_argument('--output-uri')

    args = parser.parse_args()

    dataset = DataSet.from_uri(args.dataset_uri)
    resource_dataset = DataSet.from_uri(args.resource_uri)
    output_dataset = ProtoDataSet.from_uri(args.output_uri)

    with temp_working_dir() as working_dir:
        separate_plots(dataset, args.identifier, resource_dataset, working_dir)

        filename_list = os.listdir(working_dir)

        for filename in filename_list:
            src_abspath = os.path.join(working_dir, filename)

            # useful_name = dataset.get_overlay('useful_name')[args.identifier]

            useful_name = 'a'
            relpath = os.path.join(useful_name, filename)

            # coords_value = dataset.get_overlay("coords")[args.identifier]

            output_dataset.put_item(src_abspath, relpath)
            # output_dataset.add_item_metadata(relpath, 'from', args.identifier)
            # output_dataset.add_item_metadata(relpath, 'coords', coords_value)


if __name__ == '__main__':
    main()
