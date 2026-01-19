@echo off
setlocal enabledelayedexpansion

for /f "delims=" %%i in ('python get_tool_path.py vina') do set VINA_PATH=%%i

if "%VINA_PATH%"=="" (
    echo 错误: 未找到AutoDock Vina路径，请在步骤1中配置工具路径
    exit /b 1
)

if not exist docking_results mkdir docking_results
for %%f in (pdbqt\*.pdbqt) do (
    set "name=%%~nf"
    "%VINA_PATH%" --config vina.conf --ligand "%%f" --out "docking_results\!name!_out.pdbqt" --log "docking_results\!name!.log"
)
