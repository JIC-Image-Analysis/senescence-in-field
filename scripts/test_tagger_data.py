"""Test annotation."""

import json
import argparse

import numpy as np

from jicbioimage.core.image import Image
from jicbioimage.illustrate import AnnotatedImage

def generate_test_image(image_filename):

    image = Image.from_file(image_filename)
    grayscale = np.mean(image, axis=2)

    with open(image_filename + '.json') as f:
        location_data = json.load(f)

    annotated = AnnotatedImage.from_grayscale(grayscale)
    xdim, ydim, _ = annotated.shape

    def annotate_location(location):

        yfrac, xfrac = map(float, location_data[location].split(','))
        ypos = int(ydim * yfrac)
        xpos = int(xdim * xfrac)
        for x in range(-2, 3):
            for y in range(-2, 3):
                annotated.draw_cross((xpos+x, ypos+y), color=(255, 0, 0), radius=50)


    for location in location_data:
        annotate_location(location)

    with open('/output/ann.png', 'wb') as f:
        f.write(annotated.png())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('image_filename', help='Filename of image with JSON annotation')

    args = parser.parse_args()

    generate_test_image(args.image_filename)

if __name__ == '__main__':
    main()