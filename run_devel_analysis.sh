#!/bin/bash

CONTAINER=packed-for-cluster
ARGS="file1.png file2.png"
docker run -it --rm -v `pwd`/data:/data:ro -v `pwd`/scripts:/scripts -v `pwd`/output:/output $CONTAINER $ARGS
