import configparser
import sys

import wikiToolsInit
import wikiToolsUtils

# This file accepts command-line arguments to execute various scripts and
# sequences.

config = configparser.ConfigParser()
config.read(wikiToolsInit.configFileName)

helpMessage = f"""
--init                      execute wikiToolsInit.py - initialize wikiTools.ini
                            and location of modman.jar
--wikiElements              execute {wikiToolsInit.appendWikiElements}, patch
                            the resulting files to the game, and extract-dats
                            to {wikiToolsInit.ftlDataPath}
--wikiLists                 zip {wikiToolsInit.wikiListsName}, patch
                            it to the game's files, and extract-dats to
                            .project/FTL Data
--wikiShipExport            execute wikiShipExport.py - export ship data to
                            {wikiToolsInit.wikiShipsFile}
--wikiInfo                  do --wikiLists and --wikiElements
--wikiShips                 do --wikiLists, --wikiElements, and
                            --wikiShipExport
--help                      display help message
"""

# Zip, patch, extract Append Wiki blueprintLists
def wikiBlueprintLists():
    print('Starting step 1.')
    # FIXME: is bottom statement necessary
    config.read(wikiToolsInit.configFileName)
    fileName = wikiToolsInit.wikiListsName
    directory = config[wikiToolsInit.zipPaths][wikiToolsInit.wikiLists]
    wikiToolsUtils.zipValidatePatchExtract(fileName, directory)
    print('Finished step 1.')

# Run appendWikiElements.py, zip, patch, extract Append wikiElements
def appendWikiElements():
    print('Starting step 2.')
    wikiToolsUtils.executePythonFile('./project/', wikiToolsInit.appendWikiElements)

    fileName = wikiToolsInit.wikiElementsName
    directory = config[wikiToolsInit.zipPaths][wikiToolsInit.wikiElements]
    wikiToolsUtils.zipValidatePatchExtract(fileName, directory)
    print('Finished step 2.')

# Run wikiShipExport.py
def wikiShipExport():
    print('Starting step 3.')
    wikiToolsUtils.executePythonFile('./project/', wikiToolsInit.wikiShipExport)
    print('Finished step 3.')

# Executing section
if __name__ == '__main__':
    numArgs = len(sys.argv)

    # initialize init.py
    # FIXME: slipstreamUtils.py gets KeyError for wikiTools.ini when this done
    # here instead of calling --init in wikiTools.bat

    # init.__init__()

    if numArgs > 2:
        print('More than one argument detected. Arguments ignored.')
    elif numArgs == 1:
        #default
        wikiBlueprintLists()
        appendWikiElements()
        wikiShipExport()
    elif sys.argv[1] == '--init':
        wikiToolsInit.__init__()
    elif sys.argv[1] == '--wikiInfo':
        wikiBlueprintLists()
        appendWikiElements()
    elif sys.argv[1] == '--wikiShips':
        wikiBlueprintLists()
        appendWikiElements()
        wikiShipExport()
    elif sys.argv[1] == '--wikiLists':
        wikiBlueprintLists()
    elif sys.argv[1] == '--wikiElements':
        appendWikiElements()
    elif sys.argv[1] == '--wikiShipExport':
        wikiShipExport()
    elif sys.argv[1] == '--help' or sys.argv[1] == '--h':
        print(helpMessage)
    else:
        print('Error: please enter a valid argument')
