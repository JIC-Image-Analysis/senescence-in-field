"""senescence-in-field analysis."""

import os
import logging
import argparse

import numpy as np
from skimage.morphology import disk

from jicbioimage.core.image import Image
from jicbioimage.core.transform import transformation
from jicbioimage.core.io import AutoName, AutoWrite

from jicbioimage.transform import (
    threshold_otsu,
    remove_small_objects,
    invert,
    erode_binary,
)

from jicbioimage.segment import connected_components, watershed_with_seeds

__version__ = "0.0.1"

AutoName.prefix_format = "{:03d}_"


@transformation
def identity(image):
    """Return the image as is."""
    return image


@transformation
def red_channel(image):
    """Return the red channel."""
    return image[:, :, 0]


@transformation
def green_channel(image):
    """Return the green channel."""
    return image[:, :, 1]


@transformation
def blue_channel(image):
    """Return the blue channel."""
    return image[:, :, 2]


@transformation
def difference(im1, im2):
    """Return the absolute difference."""
    return np.abs(im1 - im2)


@transformation
def fill_small_holes(image, min_size):
    aw = AutoWrite.on
    AutoWrite.on = False
    image = invert(image)
    image = remove_small_objects(image, min_size=min_size)
    image = invert(image)
    AutoWrite.on = aw
    return image


def segment(image):
    """Return field plots."""
    red = red_channel(image)
    green = green_channel(image)
    image = difference(red, green)

    mask = threshold_otsu(image)
    mask = remove_small_objects(mask, min_size=1000)
    mask = fill_small_holes(mask, min_size=100)

    seeds = erode_binary(mask, selem=disk(10))
    seeds = remove_small_objects(seeds, min_size=100)
    seeds = connected_components(seeds, background=0)

    return watershed_with_seeds(-image, seeds=seeds, mask=mask)


def analyse_file(fpath, output_directory):
    """Analyse a single file."""
    logging.info("Analysing file: {}".format(fpath))
    image = Image.from_file(fpath)

    plots = segment(image)


def analyse_directory(input_directory, output_directory):
    """Analyse all the files in a directory."""
    logging.info("Analysing files in directory: {}".format(input_directory))
    for fname in os.listdir(input_directory):
        fpath = os.path.join(input_directory, fname)
        analyse_file(fpath, output_directory)


def main():
    # Parse the command line arguments.
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_source", help="Input file/directory")
    parser.add_argument("output_dir", help="Output directory")
    parser.add_argument("--debug", default=False, action="store_true",
                        help="Write out intermediate images")
    args = parser.parse_args()

    # Create the output directory if it does not exist.
    if not os.path.isdir(args.output_dir):
        os.mkdir(args.output_dir)
    AutoName.directory = args.output_dir

    # Only write out intermediate images in debug mode.
    if not args.debug:
        AutoWrite.on = False

    # Setup a logger for the script.
    log_fname = "audit.log"
    log_fpath = os.path.join(args.output_dir, log_fname)
    logging_level = logging.INFO
    if args.debug:
        logging_level = logging.DEBUG
    logging.basicConfig(filename=log_fpath, level=logging_level)

    # Log some basic information about the script that is running.
    logging.info("Script name: {}".format(__file__))
    logging.info("Script version: {}".format(__version__))

    # Run the analysis.
    if os.path.isfile(args.input_source):
        analyse_file(args.input_source, args.output_dir)
    elif os.path.isdir(args.input_source):
        analyse_directory(args.input_source, args.output_dir)
    else:
        parser.error("{} not a file or directory".format(args.input_source))

if __name__ == "__main__":
    main()
