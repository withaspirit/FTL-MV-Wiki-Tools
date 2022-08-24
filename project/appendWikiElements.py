# -*- coding: UTF-8 -*-
import xml.etree.ElementTree as ET
import time
from pathlib import Path
import blueprintUtils as blueprintUtils

# Generates code to insert blueprintList's <name> attributes
# as elements into every blueprint that appears on the Wiki.
# It then writes that text to .append files

# files used:
# blueprints.xml (all)
# autoBlueprints.xml (all)
# dlcBlueprints.xml (some)

pathToData = blueprintUtils.pathToData

# if wikiHeading not provided, it's assumed to be the same
def getOrCreateWikiHeading(blueprint: ET.Element, nameElem: ET.Element) -> str:
    wikiHeading = nameElem.get('wikiHeading')
    if wikiHeading is None:
        wikiHeading = blueprintUtils.getTitle(blueprint)
    return wikiHeading

# TODO: better logic
def getOrCreateWikiName(blueprint: ET.Element, nameElem: ET.Element) -> str:
    wikiName = nameElem.get('wikiName')
    if wikiName is None:
        wikiName = blueprintUtils.getWikiName(blueprint)

    blueprintName = blueprint.get('name')
    if ('MODULAR' in blueprintName) and (blueprintName != 'MODULAR_STORE'):
        wikiName = blueprintUtils.modularWeaponTitle(blueprint)
    elif (blueprint.tag == 'weaponBlueprint') and ('CLONE_CANNON' in blueprintName):
        # CLONE_CANNON retains bracketed text in wikiName
        wikiName = blueprint.find('title').text
    return wikiName

def appendWikiElements(blueprint: ET.Element, nameElem: ET.Element) -> str:
    blueprintTag = blueprint.tag
    blueprintName = blueprint.get('name')
    wikiName = getOrCreateWikiName(blueprint, nameElem)
    wikiHeading = getOrCreateWikiHeading(blueprint, nameElem)
    wikiRedirect = blueprintUtils.createWikiRedirect(wikiPage, wikiHeading)

    appendText = f'''
    <mod:findName type="{blueprintTag}" name="{blueprintName}">
        <mod-append:wikiRedirect>{wikiRedirect}</mod-append:wikiRedirect>
        <mod-append:wikiName>{wikiName}</mod-append:wikiName>
        <mod-append:wikiHeading>{wikiHeading}</mod-append:wikiHeading>
        <mod-append:wikiPage>{wikiPage}</mod-append:wikiPage>'''

    if blueprintTag == 'shipBlueprint':
        teleporterLimit = nameElem.get('teleporterLimit')
        appendText += f'''
        <mod-append:teleporterLimit>{teleporterLimit}</mod-append:teleporterLimit>'''

    appendText += f'''
        <mod-append:fullURL>https://ftlmultiverse.fandom.com/wiki/{wikiRedirect.replace(' ', '_')}</mod-append:fullURL>
    </mod:findName>'''
    return appendText

def getAutoBlueprintsAppend(autoBlueprints: ET.Element) -> str:
    autoBlueprintsAppend = '\n<!-- Lists -->\n'
    blueprintListOfListPath = './/blueprintList[@name="LIST_LISTS_WIKI"]'
    blueprintListOfLists = autoBlueprints.find(blueprintListOfListPath)

    for blueprintListNameElem in blueprintListOfLists.iter('blueprintListName'):
        blueprintListName = blueprintListNameElem.text
        wikiName = blueprintListNameElem.get('wikiName')
        wikiHeading = blueprintListNameElem.get('wikiHeading')
        wikiPage = blueprintListNameElem.get('wikiPage')
        wikiRedirect = blueprintUtils.createWikiRedirect(wikiPage, wikiHeading)

        autoBlueprintsAppend += f'''
    <mod:findName type="blueprintList" name="{blueprintListName}">
        <mod:setAttributes wikiName="{wikiName}" wikiPage="{wikiPage}"/>
        <mod:setAttributes wikiRedirect="{wikiRedirect}" wikiHeading="{wikiHeading}"/>
        <mod:setAttributes fullURL="https://ftlmultiverse.fandom.com/wiki/{wikiRedirect.replace(' ', '_')}"/>
    </mod:findName>'''
    return autoBlueprintsAppend

def writeXMLAppendFile(fileName: str, fileText: str):
    fileText = f'<FTL>\n{fileText}\n</FTL>\n'
    fileText = blueprintUtils.processText(fileText)
    # make directory if not exist
    Path(blueprintUtils.wikiElementsPath).mkdir(parents=True, exist_ok=True)
    fileName = f'{blueprintUtils.wikiElementsPath}{fileName}.xml.append'
    appendFile = open(fileName, 'w', encoding='utf-8')
    appendFile.write(fileText)
    appendFile.close()

def wikiPageComment(wikiPage: str) -> str:
    return f'''\n<!--
    {wikiPage}
    https://ftlmultiverse.fandom.com/wiki/{wikiPage.replace(' ', '_')}
-->'''

# main section
# read from autoblueprints, output into append files
# FIXME: could reduce runtime by passing files instead of opening for each
# exception
if __name__ == '__main__':
    print('Creating .append files. Please wait ~10 seconds.')
    start_time = time.time()

    autoBlueprints = ET.parse(pathToData + 'autoBlueprints.xml').getroot()
    blueprints = blueprintUtils.getBlueprints()

    blueprintListsWithWikiPagePath = './/blueprintList[@wikiPage]' # has wikiPage and <name> children
    blueprintListsWithWikiPage = autoBlueprints.findall(blueprintListsWithWikiPagePath)

    blueprintsAppend = ''
    dlcBlueprintsAppend = ''
    for blueprintList in blueprintListsWithWikiPage:
        wikiPage = blueprintList.get('wikiPage')
        blueprintsAppend += wikiPageComment(wikiPage)

        # parse blueprintList nameElements; skip over ones with blueprintListName
        for nameElem in blueprintList.iter('name'):
            blueprintName = nameElem.text
            blueprint = blueprintUtils.findBlueprint(blueprints, '*', blueprintName)
            if blueprint is None:
                continue

            wikiElementsAppend = appendWikiElements(blueprint, nameElem)
            if blueprintName in blueprintUtils.dlcItems:
                dlcBlueprintsAppend += wikiPageComment(wikiPage)
                dlcBlueprintsAppend += wikiElementsAppend
            else:
                blueprintsAppend += wikiElementsAppend

    writeXMLAppendFile('blueprints', blueprintsAppend)
    writeXMLAppendFile('dlcBlueprints', dlcBlueprintsAppend)

    autoBlueprintsAppend = getAutoBlueprintsAppend(autoBlueprints)
    writeXMLAppendFile('autoBlueprints', autoBlueprintsAppend)
    print('Done creating .append files after %s seconds.' % (time.time() - start_time))
