import os
import pathlib
import time
import configparser

# The project and SlipstreamModManager must be located on the same hard drive
# for this to work
# There must be only one copy of SlipstreamModManager on your system

# Running this script for the first time may take ~2-3 minutes.
# Please report if it takes longer

# To get this file running when config.ini already exists and has its paths set, delete config.ini

drive  = pathlib.Path.home().drive

# FIXME: CHANGE THIS TO CURRENT MULTIVERSE DATA FOLDER (ASSETS NOT REQUIRED)
# IDEA: get Multiverse ZIP file with highest version number from slipstreamModManager/mods? path?
mvDataName = "Multiverse 5.3 - Data.zip"
appendWikiElements = 'appendWikiElements.py'
wikiShipExport = 'wikiShipExport.py'


#files / folders
modman = 'modman.jar'
configFileName = 'config.ini'
wikiBlueprintListsName = 'Append Wiki blueprintLists'
wikiElementsName = 'Append wikiElements'

# section names
mainPaths = 'mainPaths'
projectPaths = 'projectPaths'
zipPaths = 'zipPaths'
errors = 'errors'

#option names
slipstream = 'slipstream'
cwd = 'cwd'
# TODO: rename folder to 'FTL Dats' instead of 'FTL Data' for consistency
ftlData = 'ftlData'

project = 'project'
ftlData = 'ftlData'
wikiBlueprintListsData = 'wikiBlueprintListsData'
wikiElementsData = 'wikiElementsData'

wikiBlueprintList = 'wikiBlueprintList'
wikiElements = 'wikiElements'
ftl = 'ftl'

initFinished = 'initFinished'
locationChanged = 'locationChanged'


# process:
# run init.py -> creates config.ini (sets up automation script)
# automation script -> try to build config.ini.
def __init__():
    start_time = time.time()

    config = configparser.ConfigParser(strict=False)
    config.read(configFileName)
    try:
        if configDone(config) == False:
            initConfig(config)

        slipstreamSettingsCheck(config)
    except:
        # FIXME: not sure if safe or reachable
        raise RuntimeError("BUG STATEMENT")
        # if config.has_section(errors) == False:
        #     config.add_section(errors)
        # config[errors][initFinished] = 'false'
        # config[errors][locationChanged] = 'true'
        # writeToConfigFile(config)
        # initConfig(config)

    print('Finished initializing after %s seconds.' % (time.time() - start_time))

# Ensure that modman.cfg is initialized and change allow_zip=false to allow_zip=true
def slipstreamSettingsCheck(config: configparser.ConfigParser):
    modmanCfg = 'modman.cfg'
    modmanCfgPath = f'{config[mainPaths][slipstream]}{modmanCfg}'

    if os.path.exists(modmanCfgPath) == False:
        raise RuntimeError(f'Please run "{modman}" at least once.')

    with open(modmanCfgPath, 'r+') as file:
        fileText = file.read()
        file.seek(0)
        allowZipFalse = 'allow_zip=false'
        if allowZipFalse in fileText:
            fileText = fileText.replace(allowZipFalse, 'allow_zip=true')
            file.write(fileText)
            file.truncate()

def getFilePath(fileName: str) -> str:
    print(f'Finding location of {fileName}. Please wait.')

    # look through hard drive for modman.jar
    filePathList = []
    for path, dirs, files in os.walk(f'{drive}\\'):
        for file in files:
            if file == fileName:
                # print(path)
                filePathList.append(path)

    if len(filePathList) == 0:
        errorMessage = f'"{fileName}" not found on system. Please ensure all files are on the same hard drive.'
        raise RuntimeError(errorMessage)
    elif len(filePathList) > 1:
        filePaths = '\n'.join(filePathList)
        errorMessage = '''More than one copy of "{0}" found. Please delete
        unused copies of "{0}."\n {0} paths:\n{1}'''
        errorMessage = errorMessage.format(fileName, filePaths)
        raise RuntimeError(errorMessage)

    print(f'Found {fileName} location.')
    return filePathList[0]

def initConfig(config: configparser.ConfigParser):
    print(f'Creating {configFileName}.')

    if config.has_section(mainPaths) == False:
        config.add_section(mainPaths)
    slipstreamFilePath = ''
    if (config.has_option(errors, locationChanged) == False) or (config.getboolean(errors, locationChanged) == True):
        slipstreamFilePath = getFilePath(modman)
        config[mainPaths][slipstream] = f'{slipstreamFilePath}\\'
    else:
        slipstreamFilePath = config[mainPaths][slipstream]
    cwdPath = os.path.dirname(os.path.abspath(__file__))
    config[mainPaths][cwd] = f'{cwdPath}\\'

    # FIXME: maybe use a bunch of constants instead (assuming they don't change between iterations?)
    # only folders that could change are cwd and slipstream
    if config.has_section(projectPaths) == False:
        config.add_section(projectPaths)
    projectPath = os.path.join(cwdPath,'project\\')
    config[projectPaths][project] = projectPath
    config[projectPaths][ftlData] = os.path.join(projectPath, 'FTL Data\\data\\')
    config[projectPaths][wikiBlueprintListsData] = os.path.join(projectPath, f'{wikiBlueprintListsName}\\data\\')
    config[projectPaths][wikiElementsData] = os.path.join(projectPath, f'{wikiElementsName}\\data\\')

    if config.has_section(zipPaths) == False:
        config.add_section(zipPaths)
    config[zipPaths][wikiBlueprintList] = os.path.join(projectPath, f'{wikiBlueprintListsName}\\')
    config[zipPaths][wikiElements] = os.path.join(projectPath, f'{wikiElementsName}\\')
    config[zipPaths][ftl] = os.path.join(projectPath, 'FTL Data')

    if not config.has_section(errors):
        config.add_section(errors)
    config[errors][initFinished] = 'true'
    config[errors][locationChanged] = 'false'

    writeToConfigFile(config)

def writeToConfigFile(config: configparser.ConfigParser):
    with open(configFileName, 'w') as cfgFile:
        config.write(cfgFile)

# TODO: check in case any files lived slipstreamModmanager are moved or
# make avoid duplicating work
# Check if file locations changed and whether the locations needs to be found again
def configDone(config: configparser.ConfigParser) -> bool:
    if len(config) == 0:
        return False

    # make sure directories still exist at locations
    if config.has_section(mainPaths):
        for (key, path) in config.items(mainPaths):
            if os.path.isdir(path) == False:
                config[errors][locationChanged] = 'true'
                return False

    # when there are no changed locations, check if script already finished
    if config.has_option(errors, initFinished) and config.getboolean(errors, initFinished) == True:
        return True

    # FIXME: untested when this would be reached
    return False
