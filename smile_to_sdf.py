from rdkit import Chem
from rdkit.Chem import AllChem
import os

INPUT = "ligands.smi"
OUTDIR = "sdf"
N_CONFS = 10

os.makedirs(OUTDIR, exist_ok=True)

with open(INPUT) as f:
    for line in f:
        if not line.strip():
            continue

        parts = line.strip().split()
        smiles = parts[0]
        name = parts[1] if len(parts) > 1 else smiles.replace("/", "_")

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            print(f"[FAIL] {name}")
            continue

        mol = Chem.AddHs(mol)

        params = AllChem.ETKDGv3()
        params.randomSeed = 42

        ids = AllChem.EmbedMultipleConfs(
            mol, numConfs=N_CONFS, params=params
        )

        for cid in ids:
            AllChem.UFFOptimizeMolecule(mol, confId=cid)

        out = os.path.join(OUTDIR, f"{name}.sdf")
        w = Chem.SDWriter(out)
        for cid in ids:
            w.write(mol, confId=cid)
        w.close()

        print(f"[OK] {name}")
