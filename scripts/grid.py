"""Module for organising segmented plots into a grid."""

import numpy as np


def width(region):
    ys, xs = region.index_arrays
    w = np.max(xs) - np.min(xs)
    return w

def mean_width(plots):
    regions = [plots.region_by_identifier(i) for i in plots.identifiers]
    return sum([width(r) for r in regions]) / float(len(regions))

def grid(plots):
    """Return list of list of regions.
    """
    ydim, xdim = plots.shape
    w = mean_width(plots)
    columns = []
    for i in plots.identifiers:
        r = plots.region_by_identifier(i)
        r.identifier = i
        if len(columns) == 0:
            c = Column(w, xdim)
            c.append(r)
            columns.append(c)
            continue

        included = False
        for c in columns:
            if c.in_column(r):
                c.append(r)
                included = True
                break

        if not included:
            c = Column(w, xdim)
            c.append(r)
            columns.append(c)

    # Sort the columns left to right.
    columns.sort(key=lambda i: i.x_mean)

    for c in columns:
        # Sort the rows top to bottom.
        c.sort(key=lambda i: i.centroid[0])

    return columns

class Column(list):

    def __init__(self, width, xdim):
        self.width = width / 2
        self.xdim = xdim

    @property
    def x_mean(self):
        return sum(p.centroid[1] for p in self) / len(self)

    def in_column(self, region):
        x = region.centroid[1]
        lower = max(0, self.x_mean - self.width)
        upper = min(self.x_mean + self.width, self.xdim)
        if (x > lower) and (x < upper):
            return True
        return False
