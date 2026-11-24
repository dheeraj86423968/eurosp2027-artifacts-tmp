#!/bin/bash
# paper_v19_seeds scorer: one scoring at a time, run-major; paper_v19 evalp (+ --bundle), incidents (0.10 and current grouping); then deletes the bundle (keeps manifest/calibration/layers)
T=<SCRATCH>/seeds19; V=/var/lib/docker/volumes/pdp_pdp_data/_data; RUNP=<REPO>/artifacts/paper_v19/scripts/runp.sh
export W=$T; cd $T; mkdir -p out/train
SETS="THEIA_E5-theia CLEARSCOPE_E5-clearscope TRACE_E3-trace OPTC_H051 OPTC_H201 OPTC_H501 CADETS_E3 CARBANAKV2_EDR-h1 FIVEDIRECTIONS_E3 THEIA_E3 CLEARSCOPE_E3 CARBANAKV2_EDR-h2 CARBANAKV2_EDR-h3 ATLASV2_EDR-h1 CARBANAKV2_EDR-h4 ATLASV2_EDR-h2 CARBANAKV2_EDR-h5"
inc() { # tag rowsfile
  nice -n 15 docker run --rm -m 6g --oom-score-adj 900 -v $T:/lab -w /lab -e PYTHONPATH=/lab/code010/engine:/lab/code010/server -e PYTHONDONTWRITEBYTECODE=1 --entrypoint python pdp/server:dev inc13.py --variants V10,V19,V19id $2 > out/inc010-$1.json 2>> logs/inc-$1.log
  MEM=6g $RUNP inc13.py --variants V10,V19,V19id $2 > out/inc-$1.json 2>> logs/inc-$1.log
}
score() { # set run
  local s=$1 r=$2 b=/data/paper19s/$1/r$2/b07
  while true; do
    g=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1); m=$(free -m | awk '/Mem:/{print $7}')
    [ $g -ge 6144 ] && [ $m -ge 10240 ] && break
    echo "$(date -u +%T) scorer waiting $s r$r gpu $g ram $m" >> logs/wait.log; sleep 120
  done
  echo "$(date -u +%T) score $s r$r"
  local fail=0
  for t in "" -3att; do
    x=""; [ "$t" = -3att ] && { [ $s = CLEARSCOPE_E5-clearscope ] || continue; x="--gt-extra E5-CLEARSCOPE/node_clearscope_e5_lockwatch_0517.csv"; }
    k=$s$t-r$r
    $RUNP evalp.py $s --bundle $b --out out/res-$k.json --rows out/rows-$k.json.gz --npz out/scores-$k.npz $x < /dev/null > logs/eval-$k.log 2>&1
    rc=$?; [ $rc -ne 0 ] || [ ! -s out/res-$k.json ] && { echo "$(date -u +%T) score $k FAILED rc=$rc"; fail=1; continue; }
    [ -z "$t" ] && inc $k out/rows-$k.json.gz
    echo "$(date -u +%T) scored $k: $(grep -E 'V10:|V19:|V19id:' logs/eval-$k.log | cut -c10- | tr '\n' ' ')"
  done
  [ $fail = 1 ] && { touch out/fail-$s-r$r; return; }
  d=$V/paper19s/$s/r$r
  cp $d/train5.json out/train/train-$s-r$r.json; cp $d/b07/calibration.json out/train/calibration-$s-r$r.json; cp logs/train-$s-r$r.log out/train/ 2>/dev/null
  find $d/b07 -type f ! -name manifest.json ! -name calibration.json ! -name layers.json -delete
  touch out/done-$s-r$r
}
while true; do
  [ -f STOP ] && { echo "$(date -u +%T) scorer STOP"; break; }
  did=0
  for r in 2 3 4 5; do for s in $SETS; do
    if [ -f $V/paper19s/$s/r$r/train5.json ] && [ ! -f out/done-$s-r$r ] && [ ! -f out/fail-$s-r$r ]; then score $s $r; did=1; break 2; fi
  done; done
  if [ $did = 0 ]; then
    if [ ! -s queue.txt ] && [ -z "$(docker ps -q --filter name=s19-train)" ] && ! pgrep -f "lane19.sh [0-9]" > /dev/null; then echo "$(date -u +%T) scorer all done"; break; fi
    sleep 300
  fi
done
