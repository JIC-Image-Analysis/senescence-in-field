"""Varcan smart tool."""

import click

from dtoolcore import DataSet


@click.command()
@click.argument('dataset_uri')
@click.option('--config-path', type=click.Path(exists=True))
def main(dataset_uri, config_path=None):

    dataset = DataSet.from_uri(dataset_uri, config_path=config_path)

    def name_from_identifier(identifier):
        item_properties = dataset.item_properties(identifier)
        name = item_properties['relpath'].rsplit('.', 1)[0]
        return name

    useful_name_overlay = {
        identifier: name_from_identifier(identifier)
        for identifier in dataset.identifiers
    }

    dataset.put_overlay("useful_name", useful_name_overlay)


if __name__ == '__main__':
    main()
