#!/bin/bash
cd <SCRATCH>/lab7

for d in CADETS_E3 THEIA_E3 OPTC_H201; do
  GPU=1 MEM=24g ./run.sh prod07.py $d --name v07r --corr 1.0 --tag=-corr1 < /dev/null > corr-$d.log 2>&1; echo "$d rc=$?"
done; echo CORR-DONE
