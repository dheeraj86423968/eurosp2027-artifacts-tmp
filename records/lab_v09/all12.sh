#!/bin/bash
cd <SCRATCH>/lab9
for j in "$@"; do s=${j%%:*}; b=${j##*:}
  [ -s res12-$s.json ] && continue
  GPU=1 MEM=${MEM:-20g} ./run.sh eval12.py $s $b --out /lab/res12-$s.json --dump /lab/dump12-$s.json < /dev/null > log10-$s.log 2>&1; echo "$s rc=$?"
done; echo LANE-DONE
