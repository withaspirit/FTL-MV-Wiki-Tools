@echo off
SET PROJECT_PATH=%~dp0

cd %PROJECT_PATH%

python auto.py --init
python auto.py --fullShipExport
PAUSE
