#!/bin/bash

CONTAINER=packed-for-cluster
ARGS=155
docker run -it --rm -v `pwd`/data:/data:ro -v `pwd`/scripts:/scripts -v `pwd`/output:/output $CONTAINER $ARGS
