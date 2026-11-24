#!/bin/bash
cd <SCRATCH>/lab7

while read e d b; do
  v=$(python3 -c "import json;print(json.load(open('/var/lib/docker/volumes/pdp_pdp_data/_data/bundles/$e/$b/manifest.json'))['val_day'])")
  GPU=1 MEM=24g ./run.sh cache_val.py $e $v $b < /dev/null; echo "$e rc=$?"
done < jobsval_rest.txt
echo CACHEVAL2-DONE
