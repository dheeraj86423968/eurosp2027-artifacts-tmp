#!/bin/bash
cd <SCRATCH>/lab7
for d in CADETS_E3 THEIA_E3 OPTC_H201; do MEM=20g ./run.sh l2nodes.py $d < /dev/null > l2-$d.log 2>&1; echo "$d rc=$?"; done; echo L2-DONE
