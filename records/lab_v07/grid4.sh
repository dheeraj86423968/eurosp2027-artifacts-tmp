#!/bin/bash
cd <SCRATCH>/lab7
V=max:0:0,max:0.85:0.2,max:0.85:0.4,max:0.95:0.2,max:0.95:0.4,max:0.95:0.6
for d in CADETS_E3 THEIA_E3 OPTC_H201; do
  MEM=20g ./run.sh run_v4.py $d --learned --budget 10 --variants $V --out g4-$d.json < /dev/null > g4-$d.log 2>&1; echo "$d rc=$?"
done
echo GRID4-DONE
