"""Module for segmenting fields into plots."""

from skimage.morphology import disk

from jicbioimage.transform import (
    threshold_otsu,
    remove_small_objects,
    erode_binary,
)
from jicbioimage.segment import connected_components, watershed_with_seeds

from utils import (
    red_channel,
    green_channel,
    difference,
    fill_small_holes,
)


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
