# senescence-in-field

## Scripts

* analysis.py - DEPRECATED analysis script
* auto_overlay.py - Generate ordering and date overlays for plot images
* segment_single_file.py - PRIMARY dataset-aware tool to segment a single file
* separate_plots.py - PRIMARY dataset-aware tool to generate individual images for each plot by using segmentation to split original image into component parts
* auto_overlay.py - create overlays to determine position in field of each image, and whether it's a JPG or not
* create_exif_overlay.py - extract GPS data from each JPG image
* create_pca_component_overlay.py - use output CSV file to generate PCA components for each image and create overlay from this
* tile_images.py - create tiled plots from multiple individual images
* translate_labels.py - convert labelling of plots between this pipeline's internal labelleling and field measurement labelleling

## Introduction

This image analysis project has been setup to take advantage of a technology
known as Docker.

This means that you will need to:

1. Download and install the [Docker Toolbox](https://www.docker.com/products/docker-toolbox)
2. Build a docker image

Before you can run the image analysis in a docker container.


## Build a Docker image

Before you can run your analysis you need to build your docker image.  Once you
have built the docker image you should not need to do this step again.

A docker image is basically a binary blob that contains all the dependencies
required for the analysis scripts. In other words the docker image has got no
relation to the types of images that we want to analyse, it is simply a
technology that we use to make it easier to run the analysis scripts.

```
$ cd docker
$ bash build_docker_image.sh
$ cd ..
```

## Run the image analysis in a Docker container

The image analysis will be run in a Docker container.  The script
``run_docker_container.sh`` will drop you into an interactive Docker session.

```
$ bash run_docker_container.sh
[root@048bd4bd961c /]#
```

Now you can run the image analysis.

```
[root@048bd4bd961c /]# python scripts/analysis.py data/ output/
```

## PCA analysis

The analysis script produces a ``output/colors.csv`` file.
To perform a pca analysis on this run the command below.

```
Rscript analsis/pca.R output/colors.csv pca.png
```

Note that this requires ``ggplot2`` and ``ggfortify`` to be installed in your R.


## Manual scoring

Original raw data - ``Senescence\ scoring\ done\ by\ Tobin\ 2016.xlsx`
