#!/bin/bash
# survey_stream.sh name dump first last base test
S=<SCRATCH>/v08
n=$1; dump=$2
F=$S/${n}_ev.fifo; rm -f $F; mkfifo $F
(docker run --rm --log-driver none --name pdp-v08-$n-feed -v $dump:/dump:ro --entrypoint pg_restore postgres:17 -a -t event_table -f - /dump 2>>$S/${n}_feed.err | cut -s -f2,3,5,6,7 > $F; echo "feed done $(date +%T)" >> $S/${n}_feed.err) &
NAME=pdp-v08-$n-survey MEM=16g $S/run.sh -m pdp_server.tools.heldout_stream survey --events /work/${n}_ev.fifo \
  --first-day $3 --last-day $4 --base $5 --test $6 --out-prefix /work/$n
echo "SURVEY EXIT $? $(date +%T)"; rm -f $F
