mkdir -p docking_results

for lig in pdbqt/*.pdbqt; do
    name=$(basename "$lig" .pdbqt)
    vina \
      --config vina.conf \
      --ligand "$lig" \
      --out "docking_results/${name}_out.pdbqt" \
      --log "docking_results/${name}.log"
done
