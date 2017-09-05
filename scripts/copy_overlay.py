"""Copy overlay from one dataset to a derived dataset."""

import click

import dtoolcore


def ensure_uri(path_or_uri):

    if ':' in path_or_uri:
        return path_or_uri
    else:
        return "disk:{}".format(path_or_uri)


@click.command()
@click.argument('src_dataset_path')
@click.argument('dst_dataset_path')
@click.argument('overlay_name')
def main(src_dataset_path, dst_dataset_path, overlay_name):

    src_uri = ensure_uri(src_dataset_path)
    dst_uri = ensure_uri(dst_dataset_path)

    src_dataset = dtoolcore.DataSet.from_uri(src_uri)
    dst_dataset = dtoolcore.DataSet.from_uri(dst_uri)

    src_overlay = src_dataset.get_overlay(overlay_name)
    dst_overlay = {}

    from_overlay = dst_dataset.get_overlay('from')
    for dst_id in dst_dataset.identifiers:
        src_id = from_overlay[dst_id]
        dst_overlay[dst_id] = src_overlay[src_id]

    dst_dataset.put_overlay(overlay_name, dst_overlay)


if __name__ == '__main__':
    main()
