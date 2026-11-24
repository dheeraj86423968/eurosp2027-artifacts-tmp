#!/bin/bash
cd <SCRATCH>/lab9
for j in "$@"; do s=${j%%:*}; b=${j##*:}
  [ -s res10-$s.json ] && continue
  GPU=1 MEM=${MEM:-20g} ./run.sh eval10.py $s $b --out /lab/res10-$s.json --dump /lab/dump10-$s.json < /dev/null > log10-$s.log 2>&1; echo "$s rc=$?"
done; echo LANE-DONE
