#!/bin/bash
# runp.sh SCRIPT ARGS... : one paper_v19 script in the server image with the working-tree engine/server, low priority
W=${W:?work dir}
exec nice -n 15 docker run --rm --gpus all --cpu-shares 256 --shm-size 8g -m ${MEM:-20g} --oom-score-adj 900 --entrypoint python \
  -v pdp_pdp_data:/data:ro -v <REPO>/engine:/opt/pdp/engine:ro -v <REPO>/server:/opt/pdp/server:ro \
  -v <PIDSMAKER>/Ground_Truth/orthrus:/gt:ro -v $W:/lab -w /lab -e PYTHONPATH=/opt/pdp/engine:/opt/pdp/server -e PYTHONDONTWRITEBYTECODE=1 \
  pdp/server:dev -u "$@"
