@echo off
setlocal enabledelayedexpansion

for /f "delims=" %%i in ('python get_tool_path.py obabel') do set OBABEL_PATH=%%i

if "%OBABEL_PATH%"=="" (
    echo 错误: 未找到OpenBabel路径，请在步骤1中配置工具路径
    exit /b 1
)

if not exist pdbqt mkdir pdbqt
for %%f in (sdf\*.sdf) do (
    set "name=%%~nf"
    "%OBABEL_PATH%" "%%f" -O "pdbqt\!name!.pdbqt" --partialcharge gasteiger
)
