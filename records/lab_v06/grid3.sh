#!/bin/bash
cd <SCRATCH>/lab6
for d in CADETS_E3 THEIA_E3 OPTC_H201 OPTC_H501 OPTC_H051; do
  MEM=24g ./run.sh lab.py $d v3.json --out r3-$d.json > g3-$d.log 2> g3-$d.err
  echo "$d rc=$?"
done
echo GRID3-DONE
