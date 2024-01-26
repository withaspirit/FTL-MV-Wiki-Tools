import os
import pathlib
import time
import configparser

# Finds the location of SlipstreamModManager's modman.jar and creates
# wikiTools.ini to store its location.

# This file does set Slipstream's modman.cfg's allow_zip=true if it has not
# been done already.
# This file detects whether the project folder or Slipstream folder have been
# moved.

# REQUIREMENTS
# The project and SlipstreamModManager must be located on the same hard drive
# For this to work, there must be only one copy of SlipstreamModManager on
# your system.

# Running this for the first time may take ~2-3 minutes.
# To restart initializing wikiTools.ini, delete the file


drive  = pathlib.Path.home().drive

# NOTE: CHANGE THIS TO CURRENT MULTIVERSE ASSET + DATA ZIP FILE
# ASSET ZIP FILE UNNECESSARY IF NOT BEING USED OR ACCESSED FOR YOUR MOD
# formatted like
# multiverseFiles = ['ASSET ZIP FILE', 'DATA ZIP FILE']
multiverseFiles = ['', 'Multiverse 5.4 - Data.zip']
appendWikiElements = 'appendWikiElements.py'
wikiShipExport = 'wikiShipExport.py'
wikiShipsFile = 'wikiShips.txt'


# files / folders
modman = 'modman.jar'
configFileName = 'wikiTools.ini'
wikiListsName = 'Append Wiki blueprintLists'
wikiElementsName = 'Append wikiElements'
ftlDATPath = './project/FTL DAT/'


# section names
mainPaths = 'mainPaths'
projectPaths = 'projectPaths'
zipPaths = 'zipPaths'
initInfo = 'initInfo'

# option names
slipstream = 'slipstream'
cwd = 'cwd'

project = 'project'
ftlDAT = 'ftlDAT'
wikiListsData = 'wikiListsData'
wikiElementsData = 'wikiElementsData'

wikiLists = 'wikiLists'
wikiElements = 'wikiElements'
ftl = 'ftl'

initFinished = 'initFinished'
locationChanged = 'locationChanged'

# TODO: get Multiverse ZIP file with highest version number from slipstreamModManager/mods? path?

# Create wikiTools.ini, adjust modman.cfg settings if necessary
def __init__():
    start_time = time.time()

    config = configparser.ConfigParser(strict=False)
    config.read(configFileName)
    try:
        if configDone(config) == False:
            initConfig(config)

        slipstreamConfigCheck(config)
    except:
        raise RuntimeError('wikiToolsInit.__init__() failed.')

    print('Finished initializing after %s seconds.' % (time.time() - start_time))

# Ensure modman.cfg is initialized; change allow_zip=false to allow_zip=true
def slipstreamConfigCheck(config: configparser.ConfigParser):
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
    print(f'Finding location of {fileName}. Please wait ~3 minutes.')

    # look through hard drive for modman.jar
    filePathList = []
    for path, dirs, files in os.walk(f'{drive}\\'):
        # print(path)
        # Skip deleted files
        if f'{drive}\\$Recycle.Bin' in path:
            continue
        for file in files:
            if file == fileName:
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
    if ((config.has_option(initInfo, locationChanged) == False) or
            (config.getboolean(initInfo, locationChanged) == True)):
        slipstreamFilePath = getFilePath(modman)
        config[mainPaths][slipstream] = f'{slipstreamFilePath}\\'
    else:
        slipstreamFilePath = config[mainPaths][slipstream]
    cwdPath = os.path.dirname(os.path.abspath(__file__))
    config[mainPaths][cwd] = f'{cwdPath}\\'

    # FIXME: maybe use a bunch of constants instead
    # only folders that could change are cwd and slipstream
    if config.has_section(projectPaths) == False:
        config.add_section(projectPaths)
    projectPath = os.path.join(cwdPath,'project\\')
    config[projectPaths][project] = projectPath

    config[projectPaths][ftlDAT] = os.path.join(projectPath, 'FTL DAT\\data\\')
    config[projectPaths][wikiListsData] = os.path.join(projectPath, f'{wikiListsName}\\data\\')
    config[projectPaths][wikiElementsData] = os.path.join(projectPath, f'{wikiElementsName}\\data\\')

    if config.has_section(zipPaths) == False:
        config.add_section(zipPaths)
    config[zipPaths][wikiLists] = os.path.join(projectPath, f'{wikiListsName}\\')
    config[zipPaths][wikiElements] = os.path.join(projectPath, f'{wikiElementsName}\\')
    config[zipPaths][ftl] = os.path.join(projectPath, 'FTL DAT')

    if not config.has_section(initInfo):
        config.add_section(initInfo)
    config[initInfo][initFinished] = 'true'
    config[initInfo][locationChanged] = 'false'

    writeToConfigFile(config)

def writeToConfigFile(config: configparser.ConfigParser):
    with open(configFileName, 'w') as cfgFile:
        config.write(cfgFile)

def configDone(config: configparser.ConfigParser) -> bool:
    if len(config) == 0:
        return False

    # make sure directories in .ini file still exist at locations
    if config.has_section(mainPaths):
        for (key, path) in config.items(mainPaths):
            if os.path.isdir(path) == False:
                config[initInfo][locationChanged] = 'true'
                return False

    # when there are no changed locations, check if script already finished
    if config.has_option(initInfo, initFinished) and config.getboolean(initInfo, initFinished) == True:
        return True

    # FIXME: untested when this would be reached
    return False
