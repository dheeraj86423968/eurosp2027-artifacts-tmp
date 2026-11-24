#!/bin/bash
# finish the three failed paper5 runs (re-attempt, same seeds/protocol): score TRACE r3; train+score TRACE r5, FD r4
P=<SCRATCH>/p5
cd $P
source <(sed -n '/^V=/p;/^R=/p;/^score() {/,/^}/p' score.sh)
train() { NAME=p5-train-$1-r$2 GPU=1 ./run5.sh train5.py $1 $2 < /dev/null > logs/train-$1-r$2.log 2>&1; rc=$?; echo "$(date +%T) trained $1 r$2 rc=$rc"; }
score TRACE_E3-trace 3 /data/paper5/TRACE_E3-trace/r3/b07
train FIVEDIRECTIONS_E3 4
train TRACE_E3-trace 5
score FIVEDIRECTIONS_E3 4 /data/paper5/FIVEDIRECTIONS_E3/r4/b07
score TRACE_E3-trace 5 /data/paper5/TRACE_E3-trace/r5/b07
python3 summ5.py > logs/summ.out 2>> logs/summ.err; echo "$(date +%T) all done"
