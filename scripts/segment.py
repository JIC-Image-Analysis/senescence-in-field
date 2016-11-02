"""Module for segmenting fields into plots."""

import numpy as np
from skimage.morphology import disk

from jicbioimage.core.transform import transformation
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


@transformation
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


@transformation
def filter_sides(segmentation):
    """Remove hedges on left and right hand side.

    Also remove anything from the edge of the hedge
    to the closest edge of the image.
    """
    ydim, xdim = segmentation.shape
    mid_point = xdim // 2
    for i in segmentation.identifiers:
        region = segmentation.region_by_identifier(i)
        if region.area > 200000:
            segmentation[region] = 0
            y, x = [int(i) for i in region.centroid]
            if x < mid_point:
                # Left hand side of the hedge.
                xlim = np.min(region.index_arrays[1])
                # Using the identifiers in the region rather
                # than masking the region itself avoids the
                # issue of ending up with small cutoff left
                # overs.
                ids = np.unique(segmentation[0:ydim, 0:xlim])
                for i in ids:
                    segmentation[segmentation == i] = 0
            else:
                # Right hand side of the hedge.
                xlim = np.max(region.index_arrays[1])
                ids = np.unique(segmentation[0:ydim, xlim:xdim])
                for i in ids:
                    segmentation[segmentation == i] = 0

    return segmentation

@transformation
def filter_touching_border(segmentation):
    """Remove any plots touching top and bottom border of image."""
    ydim, xdim = segmentation.shape
    for i in segmentation.identifiers:
        region = segmentation.region_by_identifier(i)
        ys = region.index_arrays[0]
        if np.min(ys) == 0:
            segmentation[region] = 0
        if np.max(ys) == ydim - 1:
            segmentation[region] = 0
    return segmentation

@transformation
def filter_by_size(plots):
    """Remove plots the size of which lies outside particular min and max plot
    sizes."""

    #params = Parameters()
    
    identifiers = plots.identifiers

    # TODO - set relative to median?
    min_plot_size = 40000
    max_plot_size = 80000

    for identifier in identifiers:
        region = plots.region_by_identifier(identifier)
        size = region.area
        if (size < min_plot_size) or (size > max_plot_size):
            plots.remove_region(identifier)

    return plots