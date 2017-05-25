"""Create EXIF data overlay. Extracts GPS data from files."""

import json
import argparse

from dtool import DataSet

import exifread


def identifiers_where_overlay_is_true(dataset, overlay_name):

    selected = [identifier
                for identifier in dataset.identifiers
                if dataset.overlays[overlay_name][identifier]]

    return selected


def create_exif_overlay(dataset):

    useful_tags = {"GPS GPSLongitude": "x", "GPS GPSLatitude": "y"}
    overlay = {}
    for identifier in identifiers_where_overlay_is_true(dataset, "is_jpeg"):
        path = dataset.item_path_from_hash(identifier)
        with open(path, 'rb') as fh:
            tags = exifread.process_file(fh)
            overlay[identifier] = {
                name: str(tags[tag]) for tag, name in useful_tags.items()}

    return overlay


def main():
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('dataset_dir', help='Path to dataset')

    args = parser.parse_args()

    dataset = DataSet.from_path(args.dataset_dir)

    overlay = create_exif_overlay(dataset)

    # print(overlay)
    for coords in overlay.values():
        xmins = eval(coords['x'])[2]
        ymins = eval(coords['y'])[2]
        print("{},{}".format(xmins, ymins))


if __name__ == '__main__':
    main()
