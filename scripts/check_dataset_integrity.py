import os

from collections import defaultdict

import click

import dtoolcore


@click.command()
@click.argument('dataset_path')
def main(dataset_path):

    uri = "disk:{}".format(dataset_path)

    proto_dataset = dtoolcore.ProtoDataSet.from_uri(uri)

    overlays = defaultdict(dict)
    for handle in proto_dataset._storage_broker.iter_item_handles():
        identifier = dtoolcore.utils.generate_identifier(handle)
        item_metadata = proto_dataset._storage_broker.get_item_metadata(handle)
        for k, v in item_metadata.items():
            overlays[k][identifier] = v

    print overlays.keys()

    # for handle in proto_dataset._storage_broker.iter_item_handles():
    #     print(handle)

    for overlay in overlays:
        print len(overlays[overlay])

if __name__ == '__main__':
    main()
