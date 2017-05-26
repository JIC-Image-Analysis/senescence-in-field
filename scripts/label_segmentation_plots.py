
import os
import argparse

import numpy as np

from jicbioimage.core.image import Image
from jicbioimage.segment import SegmentedImage
from jicbioimage.illustrate import AnnotatedImage

from jicgeometry import Point2D

from dtoolcore import DataSet

from test_tagger_data import find_approx_plot_locs


def load_segmentation_from_rgb_image(filename):

    rgb_image = Image.from_file(filename)

    ydim, xdim, _ = rgb_image.shape

    segmentation = np.zeros((ydim, xdim), dtype=np.uint32)

    segmentation += rgb_image[:, :, 2]
    segmentation += rgb_image[:, :, 1].astype(np.uint32) * 256
    segmentation += rgb_image[:, :, 0].astype(np.uint32) * 256 * 256

    return segmentation.view(SegmentedImage)


def annotate_with_set_of_points(image, points):

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

    for loc in points:
        annotate_location(loc)

    return annotated


def label_plots(dataset):

    identifier = "384b5421bc782259b218eaab39171d51462202fd"

    segmentation_file = "/output/DJI_0118-segmented.JPG"

    segmentation = load_segmentation_from_rgb_image(segmentation_file)

    approx_plot_locs = find_approx_plot_locs(dataset, identifier)

    xdim, ydim = segmentation.shape

    def image_coords_to_rel_coords(image, point):
        ydim, xdim = image.shape
        y_abs, x_abs = point

        x_rel = float(x_abs) / xdim
        y_rel = float(y_abs) / ydim

        return Point2D(x_rel, y_rel)

    centroids = []
    for sid in segmentation.identifiers:
        c = segmentation.region_by_identifier(sid).centroid
        centroids.append(image_coords_to_rel_coords(segmentation, c))

    loc_labels = {l: str(n) for n, l in enumerate(approx_plot_locs)}

    image = Image.from_file(dataset.abspath_from_identifier(identifier))

    annotated = annotate_with_set_of_points(image, centroids)

    def rel_coords_to_image_coords(image, point):
        ydim, xdim = image.shape
        x_rel, y_rel = point

        return Point2D(int(y_rel * ydim), int(x_rel * xdim))

    for l in approx_plot_locs:
        annotated.text_at(
            loc_labels[l],
            rel_coords_to_image_coords(segmentation, l),
            size=60,
            color=(0, 255, 0))

    def closest_loc_label(p):
        dists = [(p.distance(l), l) for l in approx_plot_locs]

        dists.sort()

        return loc_labels[dists[0][1]]

    for c in centroids:
        label = closest_loc_label(c)
        annotated.text_at(
            label,
            rel_coords_to_image_coords(segmentation, c) + Point2D(20, 20),
            size=60,
            color=(0, 255, 255))

    with open('/output/ann.png', 'wb') as f:
        f.write(annotated.png())

    grayscale = np.mean(image, axis=2)
    annotated2 = AnnotatedImage.from_grayscale(grayscale)
    for sid in segmentation.identifiers:
        region = segmentation.region_by_identifier(sid)
        annotated2.mask_region(region.border.dilate(), [255, 255, 0])

    def closest_loc_label(p):
        dists = [(p.distance(l), l) for l in approx_plot_locs]

        dists.sort()

        return loc_labels[dists[0][1]]

    for c in centroids:
        label = closest_loc_label(c)
        annotated2.text_at(
            label,
            rel_coords_to_image_coords(segmentation, c) - Point2D(30, 30),
            size=60,
            color=(0, 255, 255))

    with open('/output/ann_plots.png', 'wb') as f:
        f.write(annotated2.png())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('dataset_path', help='Path to dataset')
    parser.add_argument('output_path', help='Output directory')

    args = parser.parse_args()

    dataset = DataSet.from_path(args.dataset_path)

    label_plots(dataset)

    # explore_dataset(dataset, args.output_path, n=1)


if __name__ == '__main__':
    main()
