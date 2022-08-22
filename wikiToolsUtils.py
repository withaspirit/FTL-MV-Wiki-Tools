import configparser
import shutil
import subprocess

import wikiToolsInit

# This file contains functions involving the slipstream's validate, patch,
# and extract-dats commands. Also contains functions to zip and move a folder.

config = configparser.ConfigParser()
config.read(wikiToolsInit.configFileName)

# zipMove and patchExtract steps together
def zipValidatePatchExtract(fileName: str, directory: str):
    zipMove(config[wikiToolsInit.projectPaths][wikiToolsInit.project], fileName, directory)
    zipName = f'{fileName}.zip'
    validate([zipName])
    patch([wikiToolsInit.multiverseName, zipName])
    extractDats(config[wikiToolsInit.zipPaths][wikiToolsInit.ftl])

# Zip a mod folder and move it to SlipstreamModManager/mods
# folder assumed to be in cwd
def zipMove(originalPath: str, zipFolder: str, targetPath: str):
    zipPath = shutil.make_archive(f'{originalPath}{zipFolder}', 'zip', targetPath)
    newPath = f'{config[wikiToolsInit.mainPaths][wikiToolsInit.slipstream]}/mods/{zipFolder}.zip'
    shutil.move(zipPath, newPath)

# NOTE: when there is bad syntax, subprocess.check_call will return non-zero exit status
def validate(files: list[str]):
    validateCmd = ['--validate'] + files
    executeSlipstream(validateCmd)

def patch(files: list[str]):
    patchCmd = ['--patch'] + files
    executeSlipstream(patchCmd)

# extract-dats to project/FTL Data
def extractDats(filePath: str):
    extractDatsCmd = ['--extract-dats', filePath]
    executeSlipstream(extractDatsCmd)

# Execute command line argument with SlipstreamModManager
def executeSlipstream(args: list[str]):
    slipstreamPath = config[wikiToolsInit.mainPaths][wikiToolsInit.slipstream]
    args = ['java', '-jar', wikiToolsInit.modman] + args
    subprocess.check_call(args, cwd=slipstreamPath, shell=True)

def executePythonFile(path: str, fileName: str):
    args = ['python', fileName]
    subprocess.check_call(args, cwd=path, shell=True)    
