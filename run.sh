#!/bin/bash

export PYTHONPATH=$(pwd):$(pwd)/encutils:$(pwd)/cssutils:$(pwd)/svg.charts:$PYTHONPATH
while [ 1 ] ; do
	python Main.py # | tee out.log 
	sleep 5
done
