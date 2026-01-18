@echo off
setlocal enabledelayedexpansion
if not exist docking_results mkdir docking_results
for %%f in (pdbqt\*.pdbqt) do (
    set "name=%%~nf"
    vina --config vina.conf --ligand "%%f" --out "docking_results\!name!_out.pdbqt" --log "docking_results\!name!.log"
)
