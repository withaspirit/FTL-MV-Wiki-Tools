import configparser
import init
import sys

import slipstreamUtils

## FIXME: this might not work if config.ini isn't already set up

# This file contains step1

config = configparser.ConfigParser()
config.read(init.configFileName)

# TODO: finish help message
helpMessage = """
--init
--appendElements        
--fullShipExport
--appendBlueprintLists  
--appendElements
--shipExport
--help   
"""


# Zip, patch, extract Append Wiki blueprintLists
def wikiBlueprintLists():
    print('Starting step 1.')
    # init.__init__()
    config.read(init.configFileName)
    fileName = init.wikiBlueprintListsName
    directory = config[init.zipPaths][init.wikiBlueprintList]
    slipstreamUtils.zipValidatePatchExtract(fileName, directory)
    print('Finished step 1.')

# Run appendWikiElements.py, Zip, patch, extract Append wikiElements
def appendWikiElements():
    print('Starting step 2.')
    slipstreamUtils.executePythonFile('./project/', init.appendWikiElements)

    fileName = init.wikiElementsName
    directory = config[init.zipPaths][init.wikiElements]
    slipstreamUtils.zipValidatePatchExtract(fileName, directory)
    print('Finished step 2.')

# Run wikiShipExport.py, Zip, patch, extract Append wikiElements
def wikiShipExport():
    print('Starting step 3.')
    slipstreamUtils.executePythonFile('./project/', init.wikiShipExport)
    print('Finished step 3.')  

# Executing section
if __name__ == '__main__':
    numArgs = len(sys.argv)
    if numArgs == 1:
        wikiBlueprintLists()
        appendWikiElements()
        wikiShipExport()
    else:
        if numArgs > 2:
            print('More than one argument detected. Arguments ignored.')
        if sys.argv[1] == '--init':
            init.__init__()
        elif sys.argv[1] == '--elements':
            wikiBlueprintLists()
            appendWikiElements()
        elif sys.argv[1] == '--fullShipExport':
            wikiBlueprintLists()
            appendWikiElements()
            wikiShipExport()
        elif sys.argv[1] == '--appendBlueprintLists':
            wikiBlueprintLists()
        elif sys.argv[1] == '--appendElements':
            appendWikiElements()
        elif sys.argv[1] == '--shipExport':
            wikiShipExport()
        elif sys.argv[1] == '--help':
            print(helpMessage)
        else:
            print('Error: please enter a valid argument')
 
