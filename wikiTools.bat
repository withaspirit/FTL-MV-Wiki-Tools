@echo off
SET PROJECT_PATH=%~dp0
cd %PROJECT_PATH%

python wikiToolsCLI.py --init
python wikiToolsCLI.py --wikiShips
PAUSE
