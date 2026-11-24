#!/bin/bash
# run a lab script in the server image with the working-tree code mounted
L=<SCRATCH>/lab8
G=${GPU:+--gpus all}
exec docker run --rm -i $G --shm-size 8g -m ${MEM:-24g} --oom-score-adj 800 --entrypoint python \
  -v pdp_pdp_data:/data -v <ENGINE_REPO>/engine:/opt/pdp/engine:ro -v <ENGINE_REPO>/server:/opt/pdp/server:ro \
  -v <PIDSMAKER>/Ground_Truth/orthrus:/gt:ro -v $L:/lab -w /lab -e PYTHONPATH=/opt/pdp/engine:/opt/pdp/server -e PYTHONDONTWRITEBYTECODE=1 ${JOBS:+-e JOBS=$JOBS} \
  pdp/server:dev -u "$@"
