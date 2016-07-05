"""Module with utility functions for generating annotations."""

from jicbioimage.transform import mean_intensity_projection
from jicbioimage.illustrate import AnnotatedImage

from utils import mean_plot_intensity


def get_grayscale_ann(image):
    """Return AnnotatedImage with field in grayscale."""
    grayscale = mean_intensity_projection(image)
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
