for h in 2 3 4 5; do
  until grep -q "CARBANAKV2_H$h s3 done" <WORK>/bl/pf_carb.log; do sleep 60; done
  rm -f <WORK>/bl/pf/CARBANAKV2_H$h/carbanakv2_h${h}_merged.pt; rm -rf <WORK>/bl/pf/CARBANAKV2_H$h/artifacts
  echo "$(date +%T) CARBANAKV2_H$h ProvFusion merged data deleted" >> <WORK>/bl/pf_carb.log
done
