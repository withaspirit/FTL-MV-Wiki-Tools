import configparser
import subprocess

import slipstreamUtils
import init
import sys

## FIXME: this might not work if config.ini isn't already set up

# This file contains step1

config = configparser.ConfigParser()
config.read(init.configFileName)

# TODO: finish help message
helpMessage = """
--appendElements        
--fullShipExport
--appendBlueprintLists  
--appendElements
--shipExport
--help   
"""


# Zip, patch, extract Append Wiki blueprintLists
def step1():
    print('Starting step 1.')
    init.__init__()
    fileName = init.wikiBlueprintListsName
    directory = config[init.zipPaths][init.wikiBlueprintList]
    slipstreamUtils.zipValidatePatchExtract(fileName, directory)
    print('Finished step 1.')

# Run appendWikiElements.py, Zip, patch, extract Append wikiElements
def step2():
    print('Starting step 2.')
    slipstreamUtils.executePythonFile('./project/', init.appendWikiElements)

    fileName = init.wikiElementsName
    directory = config[init.zipPaths][init.wikiElements]
    slipstreamUtils.zipValidatePatchExtract(fileName, directory)
    print('Finished step 2.')

# Run wikiShipExport.py, Zip, patch, extract Append wikiElements
def step3():
    print('Starting step 3.')
    slipstreamUtils.executePythonFile('./project/', init.wikiShipExport)
    print('Finished step 3.')  

# Executing section
if __name__ == '__main__':
    numArgs = len(sys.argv)
    if numArgs == 1:
        step1()
        step2()
        step3()
    else:
        if numArgs > 2:
            print('More than one argument detected. Arguments ignored.')
        if sys.argv[1] == '--elements':
            step1()
            step2()
        elif sys.argv[1] == '--fullShipExport':
            step1()
            step2()
            step3()
        elif sys.argv[1] == '--appendBlueprintLists':
            step1()
        elif sys.argv[1] == '--appendElements':
            step2()
        elif sys.argv[1] == '--shipExport':
            step3()
        elif sys.argv[1] == '--help':
            print(helpMessage)
        else:
            print('Error: please enter a valid argument')
 
