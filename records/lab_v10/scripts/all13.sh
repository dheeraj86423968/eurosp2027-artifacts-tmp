#!/bin/bash
cd <SCRATCH>/lab9
for s in "$@"; do
  [ -s res13-$s.json ] && continue
  GPU=1 MEM=${MEM:-18g} ./run.sh eval13.py $s --out /lab/res13-$s.json --rows /lab/rows13-$s.json.gz < /dev/null > log13-$s.log 2>&1; echo "$s rc=$?"
done; echo LANE-DONE
