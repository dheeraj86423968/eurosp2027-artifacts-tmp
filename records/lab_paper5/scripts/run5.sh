#!/bin/bash
# paper5: run a script in the server image with the 0.10 code snapshot (git archive 9b1b23f engine server) mounted.
# NAME=container name, MEM=memory limit, GPU=1 for --gpus all
P=<SCRATCH>/p5
L=<SCRATCH>/lab9
G=${GPU:+--gpus all}
case " $* " in *" TRACE_E3-trace "*) MEM=36g;; esac   # TRACE: run 1 was trained with 32g; its scoring needs > 20g
exec docker run --rm -i $G ${NAME:+--name $NAME} --shm-size 8g -m ${MEM:-24g} --oom-score-adj 800 --entrypoint python \
  -v pdp_pdp_data:/data -v $P/code/engine:/opt/pdp/engine:ro -v $P/code/server:/opt/pdp/server:ro \
  -v <PIDSMAKER>/Ground_Truth/orthrus:/gt:ro -v $L:/lab:ro -v $P:/p5 -w /p5 \
  -e PYTHONPATH=/opt/pdp/engine:/opt/pdp/server:/p5:/lab -e PYTHONDONTWRITEBYTECODE=1 \
  pdp/server:${IMAGE:-v101rc} -u "$@"
