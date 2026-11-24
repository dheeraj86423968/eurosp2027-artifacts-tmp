#!/bin/bash
cd <SCRATCH>/lab7
for d in CADETS_E3 THEIA_E3 OPTC_H201 OPTC_H501 OPTC_H051 CLEARSCOPE_E3 FIVEDIRECTIONS_E3; do
  GPU=1 MEM=24g ./run.sh prod07.py $d --name v07r < /dev/null > prod07-$d.log 2>&1; echo "$d rc=$?"
done; echo PROD07-DONE
