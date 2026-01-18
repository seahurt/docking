@echo off
setlocal enabledelayedexpansion
if not exist pdbqt mkdir pdbqt
for %%f in (sdf\*.sdf) do (
    set "name=%%~nf"
    obabel "%%f" -O "pdbqt\!name!.pdbqt" --partialcharge gasteiger
)
