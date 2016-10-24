"""Module with utility functions for generating annotations."""

from jicbioimage.transform import mean_intensity_projection
from jicbioimage.illustrate import AnnotatedImage

from utils import mean_plot_intensity, plot_identifier

import numpy as np

#def quick_grayscale_ann(image):

def get_grayscale_ann(image):
    """Return AnnotatedImage with field in grayscale."""
    grayscale = np.mean(image, axis=2)
    ann = AnnotatedImage.from_grayscale(grayscale)
    return ann


def color_in_plots(ann, image, plots):
    """Return AnnotatedImage with plots coloured in."""
    for i in plots.identifiers:
        region = plots.region_by_identifier(i)
        ann[region] = image[region]
    return ann


def outline_plots(ann, image, plots):
    """Outline plots with mean intensity colour."""
    for i in plots.identifiers:
        region = plots.region_by_identifier(i)

        red = mean_plot_intensity(image, region, 0)
        green = mean_plot_intensity(image, region, 1)
        blue = mean_plot_intensity(image, region, 2)

        color = (red, green, blue)
        ann.mask_region(region.border.dilate(7), color=color)
    return ann


def overlay_text(ann, image, plots, name):
    """Add text annotation."""
    for i in plots.identifiers:
        region = plots.region_by_identifier(i)

        red = mean_plot_intensity(image, region, 0)
        green = mean_plot_intensity(image, region, 1)
        blue = mean_plot_intensity(image, region, 2)

        offset = (region.centroid[0] - 120, region.centroid[1])
        ann.text_at(plot_identifier(name, i),
                    offset,
                    size=56,
                    center=True)

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
