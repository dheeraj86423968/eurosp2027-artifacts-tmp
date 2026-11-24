#!/bin/bash
# run python in the pdp/server image: platform code mounted read-only, work directory at /work, pdp_data at /data
S=<SCRATCH>/v08
exec docker run --rm -i --log-driver none ${NAME:+--name $NAME} --network shared_network --memory ${MEM:-20g} --memory-swap ${MEM:-20g} --oom-score-adj 800 \
  -v <ENGINE_REPO>:/src:ro -v $S:/work -v pdp_pdp_data:/data -v <PIDSMAKER>/Ground_Truth/orthrus:/gt:ro \
  ${EXTRA} -e PYTHONPATH=/src/engine:/src/server:/work -e PYTHONDONTWRITEBYTECODE=1 -w /work --entrypoint python pdp/server:dev "$@"
