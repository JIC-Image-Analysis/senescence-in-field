#!/bin/bash

IMAGE_NAME=senescence-in-field

cp ../requirements.txt $IMAGE_NAME
cd $IMAGE_NAME
docker build -t $IMAGE_NAME .
cd ../
