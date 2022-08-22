import configparser
import init
import sys

import slipstreamUtils

# This file accepts command-line arguments to execute various scripts and
# sequences

config = configparser.ConfigParser()
config.read(init.configFileName)

helpMessage = f"""
--init                      execute wikiToolsInit.py - initialize config.ini
                            and location of modman.jar
--wikiElements              execute {init.appendWikiElements}, patch the
                            resulting files to the game, and extract-dats to
                            {init.ftlDataPath}
--wikiLists                 zip {init.wikiBlueprintListsName}, patch it to the
                            game's files, and extract-dats to  FTL Data
--wikiShipExport            execute wikiShipExport.py - export ship data to
                            {init.wikiShipsFile}
--wikiInfo                  do --wikiLists and --wikiElements
--wikiShips                 do --wikiLists, --wikiElements, and
                            --wikiShipExport
--help                      display help message
"""

# Zip, patch, extract Append Wiki blueprintLists
def wikiBlueprintLists():
    print('Starting step 1.')
    # FIXME: is bottom statement necessary
    config.read(init.configFileName)
    fileName = init.wikiBlueprintListsName
    directory = config[init.zipPaths][init.wikiBlueprintList]
    slipstreamUtils.zipValidatePatchExtract(fileName, directory)
    print('Finished step 1.')

# Run appendWikiElements.py, zip, patch, extract Append wikiElements
def appendWikiElements():
    print('Starting step 2.')
    slipstreamUtils.executePythonFile('./project/', init.appendWikiElements)

    fileName = init.wikiElementsName
    directory = config[init.zipPaths][init.wikiElements]
    slipstreamUtils.zipValidatePatchExtract(fileName, directory)
    print('Finished step 2.')

# Run wikiShipExport.py
def wikiShipExport():
    print('Starting step 3.')
    slipstreamUtils.executePythonFile('./project/', init.wikiShipExport)
    print('Finished step 3.')

# Executing section
if __name__ == '__main__':
    numArgs = len(sys.argv)
    # initialize init.py
    # FIXME: slipstreamUtils.py gets KeyError for config.ini when this done here
    #   instead of calling --init in windowsScript.bat
    # init.__init__()

    if numArgs == 1:
        wikiBlueprintLists()
        appendWikiElements()
        wikiShipExport()

        if numArgs > 2:
            print('More than one argument detected. Arguments ignored.')

        # python does not have switch case in 3.9... sorry
        if sys.argv[1] == '--init':
            init.__init__()
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
