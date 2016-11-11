import os
import argparse

import numpy as np
from scipy.misc import imsave
from jicbioimage.core.image import Image

from summarise_data import load_manifest
from analysis import load_segmentation_from_rgb_image


def generate_single_image(color_image, segmentation):

    new_image = np.zeros(color_image.shape, dtype=np.uint8)

    for identifier in segmentation.identifiers:
        segment = segmentation.region_by_identifier(identifier)
        plot = color_image[segment.index_arrays]
        rgb_float = np.mean(plot, axis=0)
        rgb_int = map(int, rgb_float)
        new_image[segment.index_arrays] = rgb_int

    return  new_image.view(Image)

class AnalysisMagic(object):

    def __init__(self, manifest_data, results_root):

        self.results_root = results_root
        self.manifest_data = manifest_data

    def segmentation_filename(self, identifier):
        return os.path.join(self.results_root, identifier, 'segmentation.png')

    def input_image_filename(self, identifier):
        rrp = self.manifest_data.by_id(identifier)['relative_raw_path']
        return os.path.join('/project/raw/', rrp)

def make_boxes_images(multi_color_sets, filename):

    box_edge = 300
    box_pad = 100
    ydim = (2 * box_edge) + (2 + 1) * box_pad
    xdim = 5 * (box_edge + box_pad) + box_pad
    boxes_image = np.zeros((ydim, xdim, 3), dtype=np.uint8)

    for p in range(len(multi_color_sets[0])):
        xmin = box_pad + p * (box_edge + box_pad)
        xmax = (p + 1) * (box_edge + box_pad)
        for i, color_set in enumerate(multi_color_sets):
            ymin = box_pad + i * (box_pad + box_edge)
            ymax = (i + 1) * (box_edge + box_pad)
            boxes_image[ymin:ymax, xmin:xmax] = color_set[p]

    with open(os.path.join('/output', filename), 'wb') as f:
        f.write(boxes_image.view(Image).png())
 

def draw_pretty_images(manifest_data, results_root):

    plot_index = 10

    data_identifiers = [ '2016-06-28_DJI_0127',
                         '2016-07-08_DJI_0193',
                         '2016-07-15_DJI_0204',
                         '2016-07-22_DJI_0233',
                         '2016-07-29_DJI_0299' ]

    coords = [[2934, 1896],
              [2760, 1761],
              [2440, 1809],
              [2700, 1806],
              [2205, 1896]]


    coords2 = [[1530, 360],
               [1413, 276],
               [1074, 324],
               [1185, 183],
               [654, 300]]

    analysis = AnalysisMagic(manifest_data, results_root)

    color_sets = []
    color_sets2 = []

    #sectioned_image = np.zeros((4000, 4000, 3), dtype=np.uint8)
    xmin = coords[0][0] - 200
    xmax = xmin + 400
    ymin = coords[0][1] - 200
    ymax = ymin + 400

    for n, data_identifier in enumerate(data_identifiers):
        segmentation_filename = analysis.segmentation_filename(data_identifier)
        segmentation = load_segmentation_from_rgb_image(segmentation_filename)

        raw_image_filename = analysis.input_image_filename(data_identifier)
        print raw_image_filename
        color_image = Image.from_file(raw_image_filename)
        sectioned_image = color_image[xmin:xmax,ymin:ymax,:]

        #do_nice_things(color_image, segmentation, coords[n])
        output_image = generate_single_image(color_image, segmentation)
        with open('/output/{}.png'.format(data_identifier), 'wb') as f:
            f.write(output_image.png())

        def find_segment_color(x, y):
            identifier = segmentation[y, x]
            segment = segmentation.region_by_identifier(identifier)
            plot = color_image[segment.index_arrays]
            rgb_float = np.mean(plot, axis=0)
            rgb_int = map(int, rgb_float)

            return rgb_int

        rgb_int = find_segment_color(*coords[n])
        color_sets.append(rgb_int)

        rgb_int = find_segment_color(*coords2[n])
        color_sets2.append(rgb_int)


    make_boxes_images([color_sets, color_sets2], 'boxes.png')
    #make_boxes_images(color_sets2, 'boxes2.png')

    print sectioned_image.shape
    print sectioned_image.dtype
    #with open('/output/sectioned_image.png', 'wb') as f:
    #    f.write(sectioned_image.view(Image).png())
    #imsave('/output/sectioned_image.png', color+_


def main():

    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('project_root', help='Root of project directory.')
    parser.add_argument('analysis_name', help='Identifier for analysis.')

    args = parser.parse_args()

    manifest_data = load_manifest(args.project_root)

    results_root = os.path.join(args.project_root, 'output', args.analysis_name)

    draw_pretty_images(manifest_data, results_root)
    

if __name__ == "__main__":
    main()
