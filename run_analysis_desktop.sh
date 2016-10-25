#!/bin/bash

PROJECT=senescence-in-field
CONTAINER=packed-for-cluster
DATA_ROOT=~/sketchings/$PROJECT/input
OUTPUT=~/sketchings/$PROJECT/output
ARGS=155

docker run -it --rm -v `pwd`/scripts:/scripts -v $DATA_ROOT:/data:ro -v $OUTPUT:/output $CONTAINER $ARGS
