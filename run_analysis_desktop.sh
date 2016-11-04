#!/bin/bash

DATA=~/mnt/cluster_home/sketchings/senescence-in-field/raw
PROJECT=~/mnt/cluster_home/sketchings/senescence-in-field/
CONTAINER=senescence-in-field
docker run -t --rm -v $PROJECT:/project:ro -v $DATA:/data:ro -v `pwd`/scripts:/scripts:ro -v `pwd`/output:/output $CONTAINER python /scripts/agent.py $1
