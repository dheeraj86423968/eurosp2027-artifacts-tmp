#!/bin/bash
# run a lotl_paper script in the server image (product code mounted read-only, lab data read-only)
# usage: [GPU=1] [MEM=18g] [NAME=x] run.sh script.py args...   (outputs under the scratch work dir, mounted as /lab)
W=<SCRATCH>/lotl
C=<ENGINE_REPO>/artifacts/lotl_paper/scripts
G=${GPU:+--gpus all}
exec docker run --rm -i $G ${NAME:+--name $NAME} --shm-size 8g -m ${MEM:-18g} --oom-score-adj 1000 --entrypoint python \
  -v pdp_pdp_data:/data:ro -v <ENGINE_REPO>/engine:/opt/pdp/engine:ro -v <ENGINE_REPO>/server:/opt/pdp/server:ro \
  -v <PIDSMAKER>/Ground_Truth/orthrus:/gt:ro -v $W:/lab -v $C:/code:ro -w /lab \
  -e PYTHONPATH=/code:/opt/pdp/engine:/opt/pdp/server -e PYTHONDONTWRITEBYTECODE=1 \
  pdp/server:dev -u "$@"
