"""Automatically apply overlays to field senescence data based on file
properties."""

import os
import time
import argparse
import datetime

from collections import defaultdict

from dtool import DataSet


def path_to_date(dataset, entry):

    date = entry["path"].split(' ')[0]

    try:
        time.strptime(date, '%Y-%m-%d')
    except ValueError:
        return None

    return date


def path_to_photo_number(dataset, entry):

    try:
        no_ext, ext = os.path.splitext(entry["path"])
        number = int(no_ext.rsplit('_', 1)[1])
    except (IndexError, ValueError):
        return None

    return number


def entry_to_is_jpeg(dataset, entry):

    return entry["mimetype"] == 'image/jpeg'


def identifiers_where_overlay_is_true(dataset, overlay_name):

    selected = [identifier
                for identifier in dataset.identifiers
                if dataset.overlays[overlay_name][identifier]]

    return selected


def create_overlay_from_dataset(
    dataset,
    extraction_function
):

    new_overlay = dataset.empty_overlay()

    file_list = dataset.manifest["file_list"]

    for entry in file_list:
        value = extraction_function(dataset, entry)
        new_overlay[entry["hash"]] = value

    return new_overlay


def extract_ordering_from_dataset(
    dataset
):

    new_overlay = dataset.empty_overlay()

    date_overlay = dataset.overlays["date"]
    photo_number_overlay = dataset.overlays["photo_number"]

    dates = set(date_overlay.values()) - set([None])

    grouped_by_date = defaultdict(list)

    for identifier in identifiers_where_overlay_is_true(dataset, "is_jpeg"):
        date = date_overlay[identifier]
        photo_number = photo_number_overlay[identifier]
        if photo_number is not None and date is not None:
            item_path = dataset.item_path_from_hash(identifier)
            grouped_by_date[date].append((photo_number, identifier))

    for date, group in grouped_by_date.items():
        sorted_group = sorted(group)
        for n, pair in enumerate(sorted_group):
            _, identifier = pair
            new_overlay[identifier] = n

    dataset.persist_overlay("ordering", new_overlay, overwrite=True)


def generate_overlay_for_dataset(
    dataset,
    extraction_function,
    overlay_name
):

    new_overlay = create_overlay_from_dataset(dataset, extraction_function)
    dataset.persist_overlay(overlay_name, new_overlay, overwrite=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('dataset_path')

    args = parser.parse_args()

    dataset = DataSet.from_path(args.dataset_path)

    # generate_overlay_for_dataset(dataset, path_to_date, "date")
    # generate_overlay_for_dataset(dataset, path_to_photo_number, "photo_number")
    # generate_overlay_for_dataset(dataset, entry_to_is_jpeg, "is_jpeg")
    # extract_ordering_from_dataset(dataset)

    my_identifier = '77624f5723c5869f47b9b52e1352e55527ddfbf1'

    merged_dict = {}
    overlays = dataset.overlays
    for entry in dataset.manifest["file_list"]:
        identifier = entry["hash"]
        merged_dict[identifier] = entry
        for overlay in overlays:
            merged_dict[identifier][overlay] = overlays[overlay][identifier]

    field_number = 3

    time_point_ids = [identifier
                      for identifier in dataset.identifiers
                      if merged_dict[identifier].get('ordering', 0) == field_number]

    for identifier in time_point_ids:
        print('"{}"'.format(dataset.item_path_from_hash(identifier)))

if __name__ == '__main__':
    main()
