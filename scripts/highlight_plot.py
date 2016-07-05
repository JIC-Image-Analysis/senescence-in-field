"""Highlight a particular plot in an image."""

import os
import argparse

from jicbioimage.core.image import Image
from jicbioimage.core.io import AutoWrite

from segment import segment
from annotate import get_grayscale_ann, color_in_plots, outline_plots


def red_outline(ann, plots, plot_id):
    """Return annotated image with plot outlined in red."""
    region = plots.region_by_identifier(plot_id)
    region = region.dilate(14)
    region = region.border
    region = region.dilate(7)
    ann.mask_region(region, color=(255, 0, 0))
    return ann


def highlight_plot(input_file, ouput_file, plot_id):
    """Highlight a particular plot in a field image"""
    image = Image.from_file(input_file)

    # Debug speed up.
#   image = image[0:500, 0:500]  # Quicker run time for debugging purposes.

    name, ext = os.path.splitext(input_file)

    plots = segment(image)

    ann = get_grayscale_ann(image)
    ann = color_in_plots(ann, image, plots)
    ann = outline_plots(ann, image, plots)
    ann = red_outline(ann, plots, plot_id)

    with open(ouput_file, "wb") as fh:
        fh.write(ann.png())


def main():
    # Parse the command line arguments.
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_file", help="Input file")
    parser.add_argument("output_file", help="Output PNG file")
    parser.add_argument("plot_id", type=int, help="Output PNG file")
    args = parser.parse_args()

    AutoWrite.on = False

    highlight_plot(args.input_file, args.output_file, args.plot_id)


if __name__ == "__main__":
    main()
