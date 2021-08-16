#!/bin/bash

set -x

docker image rm -f qllabels
docker build -t qllabels .

