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
    mean_intensity_projection,
)

from jicbioimage.segment import connected_components, watershed_with_seeds
from jicbioimage.illustrate import AnnotatedImage

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

    return seeds

    return watershed_with_seeds(-image, seeds=seeds, mask=mask)


def mean_plot_intensity(image, region, channel):
    """Return the mean intensity of a color channel for a plot region."""
    ar = image[:, :, channel]
    return float(np.mean(ar[region]))


def annotate(image, plots):
    """Write out an image of the field with the plots annotated."""
    grayscale = mean_intensity_projection(image)
    ann = AnnotatedImage.from_grayscale(grayscale)
    for i in plots.identifiers:
        region = plots.region_by_identifier(i)

        ann[region] = image[region]

        red = mean_plot_intensity(image, region, 0)
        green = mean_plot_intensity(image, region, 1)
        blue = mean_plot_intensity(image, region, 2)

        color = (red, green, blue)
        ann.mask_region(region.border.dilate(7), color=color)

        offset = (region.centroid[0] - 60, region.centroid[1])
        ann.text_at("R: {:5.1f}".format(red),
                    offset,
                    size=56,
                    center=True)
        ann.text_at("G: {:5.1f}".format(green),
                    region.centroid,
                    size=56,
                    center=True)
        offset = (region.centroid[0] + 60, region.centroid[1])
        ann.text_at("B: {:5.1f}".format(blue),
                    offset,
                    size=56,
                    center=True)

    return ann

def write_csv_header(fhandle):
    line = "red,green,blue,name\n"
    fhandle.write(line)

def write_csv_row(image, plots, name, fhandle):
    line = "{red:d},{green:d},{blue:d},{name}\n"
    for i in plots.identifiers:
        region = plots.region_by_identifier(i)

        red = int(round(mean_plot_intensity(image, region, 0)))
        green = int(round(mean_plot_intensity(image, region, 1)))
        blue = int(round(mean_plot_intensity(image, region, 2)))

        d = dict(red=red, green=green, blue=blue, name=name)
        fhandle.write(line.format(**d))


def analyse_file(fpath, output_directory, csv_fhandle):
    """Analyse a single file."""
    logging.info("Analysing file: {}".format(fpath))
    image = Image.from_file(fpath)
#   image = image[0:500, 0:500]  # Quicker run time for debugging purposes.

    plots = segment(image)
    ann = annotate(image, plots)

    fname = os.path.basename(fpath)
    name, ext = os.path.splitext(fname)
    ann_fpath = os.path.join(output_directory, name + ".png")

    with open(ann_fpath, "wb") as fh:
        fh.write(ann.png())

    write_csv_row(image, plots, name, csv_fhandle)


def analyse_directory(input_directory, output_directory):
    """Analyse all the files in a directory."""
    logging.info("Analysing files in directory: {}".format(input_directory))
    csv_fname = os.path.join(output_directory, "colors.csv")
    with open(csv_fname, "w") as csv_fhandle:
        write_csv_header(csv_fhandle)
        for fname in os.listdir(input_directory):
            fpath = os.path.join(input_directory, fname)
            analyse_file(fpath, output_directory, csv_fhandle)


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
        csv_fname = os.path.join(args.output_dir, "colors.csv")
        with open(csv_fname, "w") as csv_fhandle:
            write_csv_header(csv_fhandle)
            analyse_file(args.input_source, args.output_dir, csv_fhandle)
    elif os.path.isdir(args.input_source):
        analyse_directory(args.input_source, args.output_dir)
    else:
        parser.error("{} not a file or directory".format(args.input_source))

if __name__ == "__main__":
    main()
