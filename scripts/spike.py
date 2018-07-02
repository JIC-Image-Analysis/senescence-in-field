
import dtoolcore

import click

from translate_labels import image_plot_to_rack_plot


@click.command()
@click.argument('dataset_uri')
def main(dataset_uri):

    dataset = dtoolcore.DataSet.from_uri(dataset_uri)

    pca_overlay = dataset.get_overlay('pca_component_2')
    rls_overlay = dataset.get_overlay('relative_leaf_senescence')
    date_overlay = dataset.get_overlay('date')

    print("{},{}".format("rls", "pca"))
    for identifier in dataset.identifiers:
        date = date_overlay[identifier]
        if date == '2016-07-15':
            rls = rls_overlay[identifier]
            pca = pca_overlay[identifier]
            if rls is not None and pca is not None:
                print("{},{}".format(rls, pca))
    # young_plots = ['55_24', '50_14', '54_18', '16_9', '47_14']

    # for label in young_plots:
    #     n_image, n_plot = map(int, label.split('_'))
    #     print(image_plot_to_rack_plot(n_image, n_plot))


if __name__ == '__main__':
    main()
