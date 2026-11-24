#!/bin/bash
cd <SCRATCH>/lab7
for d in THEIA_E3 OPTC_H201; do MEM=20g ./run.sh run_bl.py $d --out bl1-$d.json --save bl1-$d.npz > bl1-$d.log 2>&1; echo "$d rc=$?"; done
echo BL1-DONE
