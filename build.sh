#!/bin/bash

set -x

#cp -v ../bin/QLLABELS.py .
#cp -v ../tests .

docker image rm -f qllabels
docker build --no-cache -f Dockerfile -t "stuartlynne/qllabels:0.6" .

#rm -rf QLLABELS.py tests

