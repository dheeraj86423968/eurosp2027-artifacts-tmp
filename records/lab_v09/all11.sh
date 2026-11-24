#!/bin/bash
cd <SCRATCH>/lab9
for j in "$@"; do s=${j%%:*}; b=${j##*:}
  [ -s res11-$s.json ] && continue
  GPU=1 MEM=${MEM:-20g} ./run.sh eval11.py $s $b --out /lab/res11-$s.json --dump /lab/dump11-$s.json < /dev/null > log10-$s.log 2>&1; echo "$s rc=$?"
done; echo LANE-DONE
