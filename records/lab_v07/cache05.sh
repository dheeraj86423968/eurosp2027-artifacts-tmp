#!/bin/bash
cd <SCRATCH>/lab7
while read e d b; do GPU=1 MEM=24g ./run.sh cache_scores.py $e $d $b < /dev/null; echo "$e rc=$?"; done < jobs05.txt
echo CACHE05-DONE
