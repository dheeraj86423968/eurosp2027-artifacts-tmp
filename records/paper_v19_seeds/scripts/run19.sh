#!/bin/bash
# paper_v19_seeds training container = lab_paper5 run5.sh (0.10 code 9b1b23f, image v101rc), work dir seeds19, nice 15
P=<SCRATCH>/p5; L=<SCRATCH>/lab9; T=<SCRATCH>/seeds19
G=${GPU:+--gpus all}
case " $* " in *" TRACE_E3-trace "*) MEM=36g;; esac
exec nice -n 15 docker run --rm -i $G ${NAME:+--name $NAME} --cpu-shares 512 --shm-size 8g -m ${MEM:-24g} --oom-score-adj 800 --entrypoint python \
  -v pdp_pdp_data:/data -v $P/code/engine:/opt/pdp/engine:ro -v $P/code/server:/opt/pdp/server:ro \
  -v <PIDSMAKER>/Ground_Truth/orthrus:/gt:ro -v $L:/lab:ro -v $T:/p5 -w /p5 \
  -e PYTHONPATH=/opt/pdp/engine:/opt/pdp/server:/p5:/lab -e PYTHONDONTWRITEBYTECODE=1 \
  pdp/server:v101rc -u "$@"
