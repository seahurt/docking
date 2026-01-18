mkdir -p pdbqt

for f in sdf/*.sdf; do
    name=$(basename "$f" .sdf)
    obabel "$f" -O "pdbqt/${name}.pdbqt" \
        --partialcharge gasteiger
done
