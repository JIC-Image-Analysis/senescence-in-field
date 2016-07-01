#!/bin/bash

CONTAINER=senescence-in-field
docker run -it --rm -v `pwd`/data:/data:ro -v `pwd`/scripts:/scripts:ro -v `pwd`/output:/output $CONTAINER
