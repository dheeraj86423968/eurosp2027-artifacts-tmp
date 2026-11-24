#!/bin/bash
waitfree() { while [ "$(df --output=avail -B1 / | tail -1)" -lt $1 ]; do sleep 60; done; }
# FiveDirections ORTHRUS (needs ~12 GB of artifacts and 40 GB RAM, alone) and Velox s3, s4
waitfree 37500000000
mkdir -p <WORK>/bl/pm/FIVEDIRECTIONS_E3 && chown 1000:1000 <WORK>/bl/pm/FIVEDIRECTIONS_E3
G5="E3-FIVEDIRECTIONS/node_fivedirections_e3_excel_0409.csv E3-FIVEDIRECTIONS/node_fivedirections_e3_firefox_0411.csv"
for s in 0 1 2; do
  while docker ps --format '{{.Names}}' | grep -q '^bl-'; do sleep 30; done
  rm -rf <WORK>/bl/pm/dumps/orthrus_non_snooped_FIVEDIRECTIONS_E3_s$s
  <WORK>/bl/pm_queue_host.sh FIVEDIRECTIONS_E3 3 <PIDSMAKER>/Ground_Truth/orthrus "$G5" "orthrus_non_snooped:$s:40g"
done
rm -rf <WORK>/bl/pm/dumps/velox_FIVEDIRECTIONS_E3_s3 <WORK>/bl/pm/dumps/velox_FIVEDIRECTIONS_E3_s4
<WORK>/bl/pm_queue_host.sh FIVEDIRECTIONS_E3 3 <PIDSMAKER>/Ground_Truth/orthrus "$G5" "velox:3 velox:4"
rm -rf <WORK>/bl/pm/FIVEDIRECTIONS_E3
echo "$(date +%T) FiveDirections PIDSMaker block finished" >> <WORK>/bl/pm/queue_hosts.log
for h in 1 2 3 4 5; do
  DS=CARBANAKV2_H$h; mkdir -p <WORK>/bl/pm/$DS && chown 1000:1000 <WORK>/bl/pm/$DS
  td=$(python3 -c "import json;print(len(json.load(open('<ENGINE_REPO>/artifacts/baselines_paper/specs/pm_$DS.json'))['test_dates']))")
  PMNAME=TCFMT_$DS <WORK>/bl/pm_queue_host.sh $DS $td <WORK>/bl/conv/gt_carbanakv2_h$h "carbanakv2_edr.csv" "velox:0 orthrus_non_snooped:0 velox:1 orthrus_non_snooped:1 velox:2 orthrus_non_snooped:2"
  rm -rf <WORK>/bl/pm/$DS
done
echo "$(date +%T) pm_after finished" >> <WORK>/bl/pm/queue_hosts.log
