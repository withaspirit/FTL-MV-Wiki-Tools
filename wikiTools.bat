@echo off
SET PROJECT_PATH=%~dp0
cd %PROJECT_PATH%

python wikiToolsCLI.py --init
python wikiToolsCLI.py --wikiInfo
python wikiToolsCLI.py --wikiShipExport
PAUSE
