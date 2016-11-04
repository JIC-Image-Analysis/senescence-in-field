"""Module for segmenting fields into plots."""

import numpy as np
from skimage.morphology import disk

from jicbioimage.core.transform import transformation
from jicbioimage.transform import (
    threshold_otsu,
    remove_small_objects,
    erode_binary,
    smooth_gaussian
)
from jicbioimage.segment import connected_components, watershed_with_seeds

from utils import (
    red_channel,
    green_channel,
    blue_channel,
    abs_difference,
    fill_small_holes,
)

@transformation
def threshold_abs(image):
    return image > 20

@transformation
def median_filter(image):

    from skimage.filters.rank import median

    return median(image, disk(10))

@transformation
def local_entropy(image):
    smoothed = median_filter(image)

    diff = smoothed.astype(np.int16) - image.astype(np.int16)

    diff[np.where(diff < 0)] = 0

    return diff

def normalise_array(array):
    
    a_min = array.min()
    a_max = array.max()

    return (array - a_min) / (a_max - a_min)

def force_to_uint8(array):

    normalised = normalise_array(array)
    scaled = normalised * 255

    return scaled.astype(np.uint8)

@transformation
def sklocal(image):

    from skimage.filters.rank import entropy

    le = entropy(image, disk(5))

    return force_to_uint8(le)

@transformation
def skmean(image):

    from skimage.filters.rank import mean

    mean_filtered = mean(image, disk(30))

    print mean_filtered.min(), mean_filtered.max()

    return mean_filtered

@transformation
def segment(image):
    """Return field plots."""
    red = red_channel(image)
    green = green_channel(image)

    image = sklocal(green)
    print image.min(), image.max()
    image = skmean(image)

    #entropy = local_entropy(green)
    #smoothed = median_filter(entropy)
    #image = difference(blue_green, red)
    #image = difference(green, red)

    mask = threshold_otsu(image)

    #mask = threshold_abs(image)
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
