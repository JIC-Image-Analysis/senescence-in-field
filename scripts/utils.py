"""Utility functions."""

import numpy as np

from jicbioimage.core.io import AutoWrite
from jicbioimage.core.transform import transformation
from jicbioimage.transform import (
    invert,
    remove_small_objects,
)


def plot_identifier(name, plot_id):
    """Return file,plot_id identifier."""
    prefix, number = name.split("_")
    return "{}-{}".format(number, plot_id)


def mean_plot_intensity(image, region, channel):
    """Return the mean intensity of a color channel for a plot region."""
    ar = image[:, :, channel]
    return float(np.mean(ar[region]))


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
