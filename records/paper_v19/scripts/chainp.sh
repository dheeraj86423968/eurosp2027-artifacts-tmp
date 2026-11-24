#!/bin/bash
# paper_v19: prep (V19 for E5 ClearScope, V19id everywhere), then evalp per set (two at a time), then incidents
P=$(cd "$(dirname "$0")" && pwd); export W=${W:?work dir}; cd $W
DEV="CADETS_E3 THEIA_E3 CLEARSCOPE_E3 FIVEDIRECTIONS_E3 TRACE_E3-trace THEIA_E5-theia OPTC_H201 OPTC_H501 OPTC_H051 ATLASV2_EDR-h1 ATLASV2_EDR-h2 CARBANAKV2_EDR-h1 CARBANAKV2_EDR-h2 CARBANAKV2_EDR-h3 CARBANAKV2_EDR-h4 CARBANAKV2_EDR-h5"
ALL="$DEV CLEARSCOPE_E5-clearscope"
echo "$(date -u +%T) prep"
printf '%s\n' $ALL | xargs -P 3 -I{} bash -c "$P/runp.sh prepp.py {} > out/log-prep-{}.log 2>&1; echo \"\$(date -u +%T) prep {} rc=\$?\""
n=$(ls out/layersp-*-RP2id.json | wc -l); m=$(ls out/layers22-*-RP2.json | wc -l); echo "fitted RP2 $m RP2id $n"; [ "$n" = 17 ] && [ "$m" = 17 ] || exit 1
echo "$(date -u +%T) eval"
one() { s=$1; x=$2; t=$3; $P/runp.sh evalp.py $s --out out/res-$s$t.json --rows out/rows-$s$t.json.gz --npz out/scores-$s$t.npz ${x:+--gt-extra $x} > out/log-eval-$s$t.log 2>&1; echo "$(date -u +%T) eval $s$t rc=$? $(grep -E 'V10:|V19:|V19id:' out/log-eval-$s$t.log | sed 's/^.\{9\}//' | tr '\n' ' ')"; }
export -f one; export P
( for s in $ALL; do echo "$s"; done; echo "CLEARSCOPE_E5-clearscope E5-CLEARSCOPE/node_clearscope_e5_lockwatch_0517.csv -3att" ) | xargs -P 2 -L 1 bash -c 'one "$0" "$1" "$2"'
echo "$(date -u +%T) incidents"
$P/runp.sh inc13.py --variants V10,V19,V19id $(for s in $ALL; do echo out/rows-$s.json.gz; done) > out/inc.json 2> out/inc.log; echo "inc rc=$?"
echo "$(date -u +%T) CHAIN DONE"
