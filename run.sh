#!/bin/bash

export PYTHONPATH=$(pwd):$PYTHONPATH
while [ 1 ] ; do
	python Main.py # | tee out.log 
	sleep 3
done
