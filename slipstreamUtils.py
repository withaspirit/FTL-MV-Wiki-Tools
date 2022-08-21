import configparser
import shutil
import subprocess

import init

# This file contains functions involving the slipstream's validate, patch,
# and extract-dats commands. Also contains functions to zip and move a folder.

config = configparser.ConfigParser()
config.read(init.configFileName)

# zipMove and patchExtract steps together
def zipPatchExtract(fileName: str, directory: str):
    zipMove(config[init.projectPaths][init.project], fileName, directory)
    zipName = f'{fileName}.zip'
    validate([zipName])
    patch([init.mvDataName, zipName])
    extractDats(config[init.zipPaths][init.ftl])

# Zip a mod folder and move it to SlipstreamModManager/mods
# folder assumed to be in cwd
def zipMove(zipLocation: str, zipFolder: str, targetDirectory: str):
    zipPath = shutil.make_archive(zipFolder, 'zip', targetDirectory)
    # FIXME: is the mods config main path necessary?
    newPath = f'{config[init.mainPaths][init.slipstream]}/mods/{zipFolder}.zip'
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
    slipstreamPath = config[init.mainPaths][init.slipstream]
    
    args = ['java', '-jar', init.modman] + args
    subprocess.check_call(args, cwd=slipstreamPath, shell=True)
