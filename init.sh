#!/bin/bash

set -e
cd $(dirname $0)

if [ ! -d ${1}/common ] ; then
	echo "first arg needs to be directory where common can be found"
	exit 1
fi

for py in $(ls ${1}/common/*.py) ; do
	if [ ! -e $(basename ${py}) ] ; then
		ln -s ${py}
	fi
done


