#!/bin/bash
#
if [ $# -eq 2 ]; then
    ADDRESS=$1
else
    ADDRESS=0.0.0.0
fi
echo "Source $1 $2"

while true; do
    (echo ------; fortune -la; sleep 1;  echo ------; fortune -la; echo ) | nc -N $ADDRESS $PORT
    sleep 1
done
nc -N $ADDRESS $PORT

