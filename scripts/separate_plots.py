"""Separate individual plots."""

import os
import argparse

import numpy as np

from jicbioimage.core.image import Image
from jicbioimage.segment import SegmentedImage

from dtoolcore import DataSet, ProtoDataSet


def load_segmentation_from_rgb_image(filename):

    rgb_image = Image.from_file(filename)

    ydim, xdim, _ = rgb_image.shape

    segmentation = np.zeros((ydim, xdim), dtype=np.uint32)

    segmentation += rgb_image[:, :, 2]
    segmentation += rgb_image[:, :, 1].astype(np.uint32) * 256
    segmentation += rgb_image[:, :, 0].astype(np.uint32) * 256 * 256

    return segmentation.view(SegmentedImage)


def separate_plots(dataset, identifier, resource_dataset, working_dir):

    fpath = dataset.item_content_abspath(identifier)

    segmentation = load_segmentation_from_rgb_image(fpath)

    original_id = dataset.get_overlay('from')[identifier]

    original_fpath = resource_dataset.item_content_abspath(original_id)

    original_image = Image.from_file(original_fpath)

    sid = list(segmentation.identifiers)[2]

    region = segmentation.region_by_identifier(sid)

    output_fpath = os.path.join(working_dir, 'region.png')

    region_rgb = np.dstack([region] * 3)
    masked_image = region_rgb * original_image

    rmin, rmax = min(region.index_arrays[0]), max(region.index_arrays[0])
    cmin, cmax = min(region.index_arrays[1]), max(region.index_arrays[1])

    image_section = masked_image[rmin:rmax, cmin:cmax]

    from scipy.misc import imsave
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

    working_dir = 'output'

    separate_plots(dataset, args.identifier, resource_dataset, working_dir)


if __name__ == '__main__':
    main()
