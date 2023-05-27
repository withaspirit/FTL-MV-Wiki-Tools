import xml.etree.ElementTree as ET
import re
import os

# Contains various functions, variables, and sets for other files to use.
# FIXME: the name of this file isn't descriptive

cwd = os.path.dirname(os.path.abspath(__file__))
pathToData = os.path.join(cwd,'FTL DAT/data/')
wikiElementsPath = cwd + '\\Append wikiElements\\data\\'
wikiBlueprintListsPath = cwd + '\\Append Wiki blueprintLists\\data\\'

nonexistantBlueprints = {
    'ARTILLERY_FED',
    'ARTILLERY_FED_ENEMY',    
    'ARTILLERY_MILITIA_A',
    'ARTILLERY_FREEMANTIS_A'
}

dlcItems = {
    'BOARDER_ION',
    'ARTILLERY_FED_C',
    'LASER_CHARGEGUN_PLAYER',
    'SHOTGUN_PLAYER'
}

def getBlueprints(path: str = pathToData) -> ET.Element:
    blueprintsXML = ''
    with open(path + 'blueprints.xml', encoding='utf-8') as blueprintsFile:
        blueprintsWithVanilla = blueprintsFile.read()
        blueprintsWithoutVanilla = purgeVanillaBlueprints(blueprintsWithVanilla)
        blueprintsXML = ET.fromstring(blueprintsWithoutVanilla)
    
    blueprints = ET.ElementTree(blueprintsXML).getroot()
    return blueprints

def getDLCBlueprints(path: str = pathToData) -> ET.Element:
    blueprintsXML = ''
    with open(path + 'dlcBlueprints.xml', encoding='utf-8') as blueprintsFile:
        blueprintsWithVanilla = blueprintsFile.read()
        blueprintsWithoutVanilla = purgeDLCBlueprints(blueprintsWithVanilla)
        blueprintsXML = ET.fromstring(blueprintsWithoutVanilla)
    blueprints = ET.ElementTree(blueprintsXML).getroot()
    return blueprints

def findBlueprint(rootElement: ET.Element, searchTag: str, blueprintName: str) -> ET.Element:
    if blueprintName in nonexistantBlueprints:
        return None

    blueprintPath = f'.//{searchTag}[@name="{blueprintName}"]'
    blueprint = None
    blueprint = rootElement.find(blueprintPath)

    # blueprint != text is for when accessing text_blueprints.id
    if (blueprint is not None) and  ('Blueprint' not in blueprint.tag):
        blueprint = None
    
    # in dlcBlueprints.xml
    # TODO: try blueprintName in dlcItems:
    if blueprint is None:
        blueprint = dlcBlueprints.find(blueprintPath)
    
    # in autoBlueprints.xml
    if blueprint is None:
        # blueprint belongs to a list
        blueprintListPath = f'.//blueprintList[@name="{blueprintName}"]'
        blueprint = autoBlueprints.find(blueprintListPath)

    if blueprint is None:
        raise Exception(f'Blueprint not found: {blueprintName}')
    return blueprint

# Gets blueprint found in blueprints.xml or dlcBlueprints.xml
# FIXME: this method name isn't descriptive
def getNormalBlueprint(path: str) -> ET.Element:
    blueprint = blueprints.find(path)
    if blueprint is None:
        blueprint = dlcBlueprints.find(path)

    if blueprint is None:
        raise Exception(f'Invalid blueprintPath: {path}')
    return blueprint

def createWikiRedirect(wikiPage: str, wikiHeading: str) -> str:
    # remove brackets from drones and player weapons
    wikiHeading = removeBracketsFromTitle(wikiHeading)
    wikiRedirect = ''
    if wikiPage[-1] == '#':
        # wikiPage="Page Name#"
        wikiRedirect =  f'{wikiPage}{wikiHeading}'
    elif '#' in wikiPage:
        # wikiPage="Page Name#Heading"
        wikiRedirect = wikiPage
    else:
        # wikiPage="Heading"
        wikiRedirect = wikiHeading
    return wikiRedirect

def getWikiRedirect(wikiElement: ET.Element) -> str:
    if wikiElement.tag == 'blueprintList':
        # for blueprintLists
        return wikiElement.get('wikiRedirect')
    wikiRedirect = wikiElement.find('wikiRedirect')

    if wikiRedirect is None:
        # FIXME: not sure if this is ever activated
        print(f'wikiRedirect missing for {wikiElement.get("name")}')
        wikiRedirect = getTitle(wikiElement)
    if wikiRedirect is None:
        elementName = wikiElement.get('name')
        raise Exception(f'wikiRedirect not found for {elementName}')
    return wikiRedirect.text

def getWikiName(wikiElement: ET.Element) -> str:
    if wikiElement.tag == 'blueprintList':
        return wikiElement.get('wikiName')
    
    wikiName = wikiElement.find('wikiName')
    if wikiName == None:
        displayName = getTitle(wikiElement)
    else:
        displayName = wikiName.text
    return displayName

def getTitle(blueprint: ET.Element) -> str:
    titleElement = getElementClassOrTitle(blueprint)
    
    # Dealing with <title> that has 'id' attribute
    # if it has an 'id' attribute, access it from text_blueprints.xml
    if not titleElement.get('id'):
        title = titleElement.text    
    else: 
        id = titleElement.get('id')
        # title in text_blueprints
        textBlueprint = text_blueprints.find(f'.//text[@name="{id}"]')
        if textBlueprint is None:
            raise Exception(f'Unhanded blueprint relying on id: blueprint: {blueprint.get("name")}') 
        title = textBlueprint.text

    title = removeBracketsFromTitle(title)
    return title

# class for shipBlueprint, title for all else
def getElementClassOrTitle(wikiElement: ET.Element) -> ET.Element:
    classOrTitle = ''
    if wikiElement.tag == 'shipBlueprint':
        classOrTitle = wikiElement.find('name')
    else:
        classOrTitle = wikiElement.find('title')
    
    if classOrTitle is None:
        elementName = wikiElement.get('name')
        raise Exception(f'Class or Title not found for {elementName}')
    return classOrTitle

def formatCrewBlueprintLink(wikiRedirect: str, wikiName: str, customName: str) -> str:
    if customName is None or 'Unique' in wikiRedirect:
        return formatBlueprintLink(wikiRedirect, wikiName)
    return f"{formatBlueprintLink(wikiRedirect, wikiName)} '{customName}'"


def formatBlueprintLink(wikiRedirect: str, wikiName: str) -> str:
    blueprintString = ''
    displayName = wikiName
    if wikiRedirect == displayName:
        blueprintString += f'[[{displayName}]]'
    else:
        blueprintString += f'[[{wikiRedirect}|{displayName}]]'
    return blueprintString

# one or more characterSequence in brackets followed or preceded by a space    
regexp = re.compile(' ?\[[-\w\. ]+\] ?')
def detectBracketedPart(title: str):
    return regexp.search(title)    

def removeBracketsFromTitle(title: str) -> str:
    match = detectBracketedPart(title)
    if match:
        partToRemove = match.group(0)
        title = title.replace(partToRemove, '')
    return title

modularWeaponEffects = {
    'BIO': 'Rad',
    'COOLDOWN': 'Cooldown',
    'LOCKDOWN': 'Lockdown',
    'PIERCE': 'Pierce',
    'STUN': 'Neural',
    'FIRE': 'Firestarter',
    'HULL': 'Hullbuster',
    'ACCURACY': 'Accuracy',
    'POWER': 'Power'
}

# modular weapons formatted like:
# MODULAR_WEAPONTYPE_MOD1
# MODULAR_WEAPONTYPE_MOD1_MOD2
def modularWeaponTitle(blueprintElem: ET.Element) -> str:
    blueprintName = blueprintElem.get('name')
    blueprintTitle = blueprintElem.find('title').text

    # replace base in blueprintName
    weaponMods = blueprintName.replace('_BASE', '').split('_')
    numMods = len(weaponMods) - 2
    if numMods == 0:
        return f'{blueprintTitle} Base'

    titleArray = blueprintTitle.split(' ')
    newTitle = titleArray[0]
    if numMods >= 1:
        newTitle += f' {modularWeaponEffects[weaponMods[2]]}'
    if numMods > 1:
        newTitle += f' + {modularWeaponEffects[weaponMods[3]]}'
    return f'{newTitle} {titleArray[1]}'

# Cleans up text
# Wiki uses '🗲' and '↑', XML uses &amp; instead of '&'
def processText(text: str) -> str:
    # below two statements commented to match Wiki better
    # text = text.replace('Mk.', 'MK')
    # text = text.replace('Mk.', 'MK')
    text = text.replace('&', '&amp;') # XML doesn't accept '&' characters 
    text = text.replace('†', '🗲')
    text = text.replace('™', '↑')
    return text

# exclude text between startText and endText
def replaceText(blueprintsText: str, startText: str, endText: str) -> str:
    startIndex = blueprintsText.find(startText)
    endIndex = blueprintsText.find(endText)

    if (startIndex == -1 | endIndex == -1):
        errorText = 'Text unable to be purged.'
        if startIndex == -1:
            errorText += ' Start index not found.'
        if endIndex == -1:
            errorText += ' End index not found.'
        raise Exception(errorText)

    return blueprintsText[:startIndex] + blueprintsText[endIndex:]   

def purgeVanillaBlueprints(blueprintsText: str) -> str:
    vanillaStartText = '''<!-- Customization possibilities -->'''
    vanillaEndText = '''<!--
/////////////
	KEY
/////////////

1. Crew
2. Systems
3. Hidden Augments
4. Augments
5. Weapons
6. Drones
7. Artillery and Surges
9. Player Ships
-->'''
    return replaceText(blueprintsText, vanillaStartText, vanillaEndText)

def purgeDLCBlueprints(blueprintsText: str) -> str:
    start = '<!-- Copyright (c) 2012 by Subset Games. All rights reserved -->'
    end = '<weaponBlueprint name="SHOTGUN_PLAYER">'
    return replaceText(blueprintsText, start, end)

blueprints = getBlueprints()
dlcBlueprints =  getDLCBlueprints()
autoBlueprints = ET.parse(pathToData + 'autoBlueprints.xml').getroot()
text_blueprints = ET.parse(pathToData + 'text_blueprints.xml').getroot()
