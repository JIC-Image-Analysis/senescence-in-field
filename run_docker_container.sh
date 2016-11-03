#!/bin/bash

DATA=~/mnt/cluster_home/sketchings/senescence-in-field/raw
CONTAINER=senescence-in-field
docker run -it --rm -v $DATA:/data:ro -v `pwd`/scripts:/scripts:ro -v `pwd`/output:/output $CONTAINER
