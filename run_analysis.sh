#!/bin/bash

CONTAINER=packed-for-cluster
COMMAND='python /scripts/agent.py'
docker run -it --rm -v `pwd`/data:/data:ro -v `pwd`/output:/output $CONTAINER moreargs
