#!/usr/bin/env python
"""senescence-in-field analysis."""

import os
import logging
import argparse

import numpy as np

from jicbioimage.core.image import Image
from jicbioimage.core.io import AutoName, AutoWrite
from jicbioimage.core.util.color import identifier_from_unique_color
from jicbioimage.segment import SegmentedImage

#from jicparameters import Parameters

from segment import (
    segment, 
    filter_sides, 
    filter_touching_border, 
    filter_by_size
)

from annotate import (
    get_grayscale_ann,
    color_in_plots,
    outline_plots,
    overlay_text,
)

from utils import mean_plot_intensity, plot_identifier

__version__ = "0.0.1"

AutoName.prefix_format = "{:03d}_"


def write_csv_header(fhandle):
    line = "red,green,blue,name,identifier\n"
    fhandle.write(line)


def write_csv_row(image, plots, name, fhandle):
    line = "{red:d},{green:d},{blue:d},{name},{identifier}\n"
    for i in plots.identifiers:
        region = plots.region_by_identifier(i)

        red = int(round(mean_plot_intensity(image, region, 0)))
        green = int(round(mean_plot_intensity(image, region, 1)))
        blue = int(round(mean_plot_intensity(image, region, 2)))
        identifier = plot_identifier(name, i)

        d = dict(red=red,
                 green=green,
                 blue=blue,
                 name=name,
                 identifier=identifier)
        fhandle.write(line.format(**d))



def save_segmented_image_as_rgb(segmented_image, filename):

    segmentation_as_rgb = segmented_image.unique_color_image

    with open(filename, 'wb') as f:
        f.write(segmentation_as_rgb.png())

def load_segmentation_from_rgb_image(filename):

    rgb_image = Image.from_file(filename)

    ydim, xdim, _ = rgb_image.shape

    segmentation = np.zeros((ydim, xdim), dtype=np.uint32)

    segmentation += rgb_image[:,:,2]
    segmentation += rgb_image[:,:,1].astype(np.uint32) * 256
    segmentation += rgb_image[:,:,0].astype(np.uint32) * 256 * 256

    return segmentation.view(SegmentedImage)

def analyse_file(fpath, output_directory, csv_fhandle, name=None):
    """Analyse a single file."""
    logging.info("Analysing file: {}".format(fpath))
    image = Image.from_file(fpath)

    # Debug speed up.
#   image = image[0:500, 0:500]  # Quicker run time for debugging purposes.

    fname = os.path.basename(fpath)
    if name is None:
        name, ext = os.path.splitext(fname)

    plots = segment(image) # 26s
    plots = filter_sides(plots) # +7s
    plots = filter_touching_border(plots) #+6s
    plots = filter_by_size(plots)

    segmentation_filename = os.path.join(output_directory, 'segmentation.png')
    save_segmented_image_as_rgb(plots, segmentation_filename)

    false_color_filename = os.path.join(output_directory, 'false_color.png')
    with open(false_color_filename, 'wb') as f:
        f.write(plots.png())

    # test_output_fn = os.path.join(output_directory, 'test.png')
    # with open(test_output_fn, 'wb') as f:
    #     f.write(segmentation.png())

    # print('time to stop')
    # sys.exit(0)

    # Experimenting...
    # import grid
    # from jicbioimage.core.util.color import pretty_color_from_identifier
    # ydim, xdim = plots.shape
    # columns = grid.grid(plots)
    # ann = get_grayscale_ann(image)
    # for i, c in enumerate(columns):
    #     color = pretty_color_from_identifier(i)
    #     for j, r in enumerate(c):
    #         ann.text_at("{},{}".format(i, j), r.centroid,
    #                     color=color, size=60, center=True)
    #     for i in range(3):
    #         ann.draw_line((0, c.x_mean - i), (ydim-1, c.x_mean - i), color)
    #         ann.draw_line((0, c.x_mean + i), (ydim-1, c.x_mean + i), color)

    # ann = get_grayscale_ann(image) # + 2 min 20s / now +2s
    # ann = color_in_plots(ann, image, plots)  # +4s
    # ann = outline_plots(ann, image, plots) # +10s
    # ann = overlay_text(ann, image, plots, name) # +11s

    # ann_fpath = os.path.join(output_directory, name + ".png")
    # with open(ann_fpath, "wb") as fh:
    #     fh.write(ann.png())

#   write_csv_row(image, plots, name, csv_fhandle)


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
