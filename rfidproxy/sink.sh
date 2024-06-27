#!/bin/bash
#

if [ $# -eq 2 ]; then
    ADDRESS=$1
    PORT=$2
else
    ADDRESS=127.0.0.1
    PORT=5085
fi
echo "Sink $1 $2"
set -x

#nc -kl $ADDRESS $PORT 
ncat -l $PORT --keep-open --exec "/bin/cat"

