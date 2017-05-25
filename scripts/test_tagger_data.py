"""Test annotation."""

import os

import json
import argparse

import numpy as np

from jicbioimage.core.image import Image
from jicbioimage.illustrate import AnnotatedImage

from dtoolcore import DataSet

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


def annotate_single_identifier(dataset, identifier, output_path):
    file_path = dataset.abspath_from_identifier(identifier)

    image = Image.from_file(file_path)
    grayscale = np.mean(image, axis=2)

    annotated = AnnotatedImage.from_grayscale(grayscale)
    xdim, ydim, _ = annotated.shape

    def annotate_location(fractional_coords):

        xfrac, yfrac = fractional_coords

        ypos = int(ydim * xfrac)
        xpos = int(xdim * yfrac)
        for x in range(-2, 3):
            for y in range(-2, 3):
                annotated.draw_cross(
                    (xpos+x, ypos+y),
                    color=(255, 0, 0),
                    radius=50
                )

    for loc in find_approx_plot_locs(dataset, identifier):
        annotate_location(loc)

    output_basename = os.path.basename(file_path)
    full_output_path = os.path.join(output_path, output_basename)
    with open(full_output_path, 'wb') as f:
        f.write(annotated.png())


def identifiers_where_overlay_is_true(dataset, overlay_name):

    overlays = dataset.access_overlays()

    selected = [identifier
                for identifier in dataset.identifiers
                if overlays[overlay_name][identifier]]

    return selected


def show_tag_locations(dataset, output_path):

    sample_id = "946f9d441234724f024d13d6b5c322bb8708f3d1"

    ids_of_interest = identifiers_where_overlay_is_true(dataset, "is_jpeg")

    for identifier in ids_of_interest[:5]:
        annotate_single_identifier(dataset, identifier, output_path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('dataset_path', help='Path to dataset')
    parser.add_argument('output_path', help='Output directory')

    args = parser.parse_args()

    dataset = DataSet.from_path(args.dataset_path)

    show_tag_locations(dataset, args.output_path)


if __name__ == '__main__':
    main()
