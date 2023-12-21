import xml.etree.ElementTree as ET
import os
import re
import json

# IDEA: match req to bracketed text in the 'text' element
# EX: req="BLUELIST_CREW_NOFIRE" -> <text>(Fireproof Crew)....</text>
# Note to self: reqs that are not in autoBlueprint.xml or blueprints.xml are found in "hyperspace.xml"
# try getting categories for stuff from autoBlueprints.xml or hyperspace.xml

# req cases
# normal req: "engi", "LIST_CREW_MEDICAL", etc
# different level reqs: req="meday" with lvl="2" and lvl="3"; req="rep_orchid", lvl=....
# weapon, ammo count: (for anything requiring ammo like MISSILE_WEAPONS_:
# ex: (QUEST_MANTIS_INVASION): (2 Fire Bombs) Teleport fire bombs into key structures.

# current working directory
cwd = os.path.dirname(os.path.abspath(__file__)) + "\\"
# have THE FTL DAT file unzipped in this folder
dataDir = 'FTL DAT ZIP\\data\\'
# create file path
dataPath = cwd + dataDir

fileNames = [
    "dlcEvents.xml.append",
    "dlcEvents_anaerobic.xml.append",
    "dlcEventsOverwrite.xml.append",
    "events.xml.append",
    "events_abandoned.xml",
    "events_ancient.xml",
    "events_anomaly.xml",
    "events_augmented.xml",
    "events_boons.xml",
    "events_boss.xml.append",
    "events_civilian.xml",
    "events_coalition.xml",
    "events_crystal.xml.append",
    "events_cultist.xml",
    "events_curator.xml",
    "events_defeat.xml",
    "events_droppoint.xml",
    "events_duskbringer.xml",
    "events_ellie.xml",
    "events_engi.xml.append",
    "events_estate.xml",
    "events_federation.xml",
    "events_finalboss.xml",
    "events_fleet.xml",
    "events_freemantis.xml",
    "events_fuel.xml.append",
    "events_gb.xml",
    "events_generic.xml",
    "events_ghost.xml",
    "events_guards.xml",
    "events_hektar.xml",
    "events_imageList.xml.append",
    "events_jukebox.xml",
    "events_leech.xml",
    "events_lightspeed.xml",
    "events_lostsun.xml",
    "events_mantis.xml.append", # not well formed, remove ""OLD ... on line 506
    "events_mechanical.xml",
    "events_morality.xml",
    "events_multiverse.xml",
    "events_nebula.xml.append",
    "events_nexus.xml",
    "events_orchid.xml",
    "events_outposts.xml",
    "events_piracy.xml",
    "events_pirate.xml.append",
    "events_rebel.xml.append",
    "events_rock.xml.append",
    "events_ruins.xml",
    "events_salvaging.xml",
    "events_separatist.xml",
    "events_shells.xml",
    "events_ships.xml.append",
    "events_siren.xml",
    "events_slug.xml.append",
    # "events_socialize.xml", # unnecessary
    "events_spider.xml",
    "events_standard.xml",
    # "events_storage.xml",
    "events_transports.xml",
    "events_trapper.xml",
    "events_zoltan.xml.append",
    "newEvents.xml.append"
]

# AKA tags to look at
tagsWithTextChildren = {
    'choice',
    'event',
    'eventList',
    'loadEvent',
    'loadEventList',
}

eventTypes = {
    'event',
    'eventList',
}

invalidsReqs = {
    'ach_',
    'loc_',
    'SEC ',
    'juke',
    'coor', # coords
    'COOR',
    'prof'
}


# events to exclude loading when parsing through events
# only want these being displayed once
# how do i tell which one of these events are recursive text without going through
# each of the them individually
# on the wiki, some events have their own page, while other events are only used within other events and are on the same page as those events

# elem.tag: attribute:, attribute: ...
# if attribute = "load"

# attriutesToSkip = {
#     'hidden',

# }

# ownpage: 
# SHIP_NEMESIS?

eventsToSkip = {
    'COMBAT_CHECK',
    'COMBAT_CHECK_FLAGSHIP',
    'STORAGE_CHECK',

    'START_BEACON_REAL',
    'SYLVAN_NORMAL',
    
    'COMBAT_CHECK_TOGGLE_LOAD',
    'REROUTE_MENU',
    'DETECTIVE_EVIDENCE_MENU_LOAD',
    'TRUE_VICTORY_LOAD',
    'LOAD_ATLAS',
    'LOAD_ATLAS_MARKER',
    'ATLAS_MENU',
    'ATLAS_MENU_NOEQUIPMENT',

    'LANIUS_TRADER_LIST',
    'LANIUS_TRADER_LIST2', 
    'LANIUS_TRADER',

    'HIGH_SCAN_TERRAFORMING'

    'THE_JUDGES_ZOLTAN_ADVICE',
    'LAST_STAND_START_2',
    'SLAVER_BETRAYAL_SLUG_BETRAY',
    'GUARD_ESCAPE',
    'GUARD_MIND',
    'GUARD_CLOAK',
    'GUARD_CIVILIAN_INTERACT',
    'GUARD_LEECH_INTERACT',

    'STORE_LOAD_ZOLTAN',
    'STORE_LOAD_GENERIC',
    'STORE_LOAD_ENGI',
    'STORE_LOAD_CRYSTAL',
    'STORE_LOAD_NOSYS',
    'STORE_LOAD_FREEMANTIS',
    'STORE_LOAD_ORCHID',
    'STORE_LOAD_MANTIS',
    'STORE_LOAD_MERCHANTS_LASERS',
    'STORE_LOAD_MERCHANTS_MISSILES',
    'STORE_LOAD_MERCHANTS_IONS',
    'STORE_LOAD_CRYSTAL_MORECRYSTAL',

    'EMPTY_STATION2',
    'PIRACY_LIST',
    'PIRACY_LIST_GENERIC',
    # 'ITEMS_ROCK',
    # 'ITEMS_ROCKHOME',

    # eventLists
    'EXIT_LIST_CIVILIAN',
    'EXIT_LIST_ZOLTAN'
}


textListsToSkip = {
    'TEXT_LIGHTSPEED',
    'TEXT_ENCOUNTER_REBEL',
}

excludedLoadEvents  = {
    'COMBAT_CHECK' : 'COMBAT_CHECK',
    'COMBAT_CHECK_FLAGSHIP': 'COMBAT_CHECK_FLAGSHIP',
    'COMBAT_CHECK_FAIL' : 'COMBAT_CHECK_FAIL',
    'LOAD_ATLAS' : 'LOAD_ATLAS',
    'STORAGE_CHECK_AUG_PANDORA_OPEN' : 'STORAGE_CHECK_AUG_PANDORA_OPEN',
    'STORAGE_CHECK' : 'STORAGE_CHECK',
    'REFUGEE_TRADER' : 'REFUGEE_TRADER', # missing
    'TUTORIAL_PART0' : 'TUTORIAL_PART0', # causes glitch
    'ROCK_SLUG_ARGUMENT_NEBULA' : 'ROCK_SLUG_ARGUMENT_NEBULA', # error
    'BOARDERS_MANTIS' : 'BOARDERS_MANTIS', # TODO look
    'BOARDERS_ZOLTAN' : 'BOARDERS_ZOLTAN',
    'MORALITY_UPDATE_GENERAL' : 'MORALITY_UPDATE_GENERAL',
    # ????
    'NEUTRAL_ROCKHOME_GENERIC' : 'NEUTRAL_ROCKHOME_GENERIC',
    'NEUTRAL_ROCKHOME_UNIQUE' : 'NEUTRAL_ROCKHOME_UNIQUE',
    # 'HOSTILE_ROCKHOME',
    # 'ITEMS_ROCKHOME',
}

falseEventNames = {
    'SAVE_CIVILIAN_LIST' : 'SAVE_CIVILIAN_LIST_LANIUS', # missing
}


# blue options
reqEventMap = {}
reqNameMap = {}
eventNameIndex = {}
dummyElement = ET.Element('dummy')

# watchout: MAGIC_HAT

with open('utils\\eventNameIndex.json') as file:
    eventNameIndex = json.load(file)

def findElementByName(fileElement : ET.Element, tag : str, name : str):
    if fileElement == dummyElement:
        fileNameList = eventNameIndex[name]
        if fileNameList is None:
            return ''
        fileElement = ET.parse(dataPath + fileNameList[0]).getroot()

    elems = fileElement.findall(f".//{tag}[@name='{name}']")
    if len(elems) > 0:
        # return last version of element
        return elems[len(elems) - 1]

# do in-file and other files search separately to optimize performance
def getEvent(fileElement : ET.Element, name : str):
    for tagType in eventTypes:
        newEventElem = findElementByName(fileElement, tagType, name)
        if newEventElem is not None:
            return newEventElem

    for tagType in eventTypes:
        newEventElem = findElementByName(dummyElement, tagType, name)
        if newEventElem is not None:
            return newEventElem

    raise Error(f'No event found: {name}')
    return None

# TODO: make this work
def checkEventName(eventName : str, eventSet : set) -> str:
    return eventName

# Adjust indent when finding recursive event
defaultIndent = '*'

def createIndent(indent : str, indentLevel : int):
    return '\n' + (indent * (indentLevel))

# indent level is 0 by default
# get the 'text' element from every event, choice, or eventList within an eventType
parenthesizedTextRegexp = re.compile('(?<=\()(.*?)(?=\))') # text between brackets
def getChildText(element : ET.Element, reqSet : set, eventSet : set, fileElement : ET.Element, indentLevel : int) -> str:
    textToAdd = ''
    # print(ET.tostring(element, method='xml'))
    # TODO: revisit

    if element.tag in eventTypes:

        eventName = element.get('name')
        # should eventName and loadAttr be exclusive? loadAttr could be a textList
        # TODO: find a better way to check this
        if eventName is not None:
            # print('event: ' + eventName)
            textToAdd += createIndent(defaultIndent, indentLevel)
            textToAdd += f'{element.tag}: '

            if eventName in eventSet:
                textToAdd += eventName
                return textToAdd
                      
            if eventName in excludedLoadEvents:
                textToAdd += excludedLoadEvents[eventName]
                return textToAdd
            elif eventName in eventsToSkip and len(eventSet) != 0:
                textToAdd += eventName
                return textToAdd
     
            eventSet.add(eventName)

            if eventName in falseEventNames:
                eventName = falseEventNames[eventName]
            textToAdd += eventName
        

    # TODO: put this closer to textList?
    loadAttr = None
    if element.tag in eventTypes:
        loadAttr = element.get('load')
    if element.tag == 'loadEvent':
        # print('loadEvent: ' + element.text)
        loadAttr = element.text
    elif element.tag == 'loadEventList':
        loadAttr = element.get('default')
    if loadAttr is not None:
        loadText = createIndent(defaultIndent, indentLevel)
        loadText += f'load {element.tag}: '

        if loadAttr in eventSet:
            return loadText + loadAttr
        # textToAdd += createIndent(defaultIndent, indentLevel + 1)
        # textToAdd += 'event: '
        if loadAttr in excludedLoadEvents:
            return loadText + excludedLoadEvents[loadAttr]
        elif loadAttr in eventsToSkip and len(eventSet) != 0: # events to exclude loading, make sure not the first event
            return loadText + loadAttr

        if loadAttr in falseEventNames:
            loadAttr = falseEventNames[loadAttr]

        # print(loadAttr)
        newEventElem = getEvent(fileElement, loadAttr)
        textToAdd += getChildText(newEventElem, reqSet, eventSet, fileElement, indentLevel)
        eventSet.add(loadAttr)

    textElem = element.find('text')
    textElemText = ''
    if textElem is not None:
        if textElem.text is not None:
            # append text with indent
            textElemText = textElem.text
            textToAdd += createIndent(defaultIndent, indentLevel)
            textToAdd += f"''{textElem.text}''"
        
        # textList
        loadAttr = textElem.get('load')
        if loadAttr is not None and len(loadAttr) > 0:
            textToAdd += createIndent(defaultIndent, indentLevel)
            textToAdd += f'textList: {loadAttr}'
            textListElem = findElementByName(fileElement, 'textList', loadAttr)
            if textListElem is None:
                textListElem = findElementByName(dummyElement, 'textList', loadAttr)

            for elem in textListElem.iter('text'):
                textToAdd += createIndent(defaultIndent, indentLevel + 1)
                textToAdd += f"''{elem.text}''"

    # build list of req for blueOptionNames.json
    reqText = element.get('req')
    if reqText is not None and len(reqText) > 0:
        # prevent reqs with 'loc_' and 'ach_' from appearing
        if reqText[:4] not in invalidsReqs:
            reqSet.add(reqText)

            # get blue option name
            if (len(textElemText) > 0) and textElemText[:1] == '(':
                if reqText not in reqNameMap.keys():
                    reqNameMap.update({reqText : []})
                match = parenthesizedTextRegexp.search(textElemText)
                if match:
                    reqNameMap[reqText].append(match.group(0))

            #   for tracking when no name used
            #   if (len(textElemText) > 0):
            #         if reqText not in reqNameMap.keys():
            #             reqNameMap.update({reqText : []})
            #         if textElemText[:1] == '(':
            #             match = parenthesizedTextRegexp.search(textElemText)
            #             if match:
            #                 reqNameMap[reqText].append(match.group(0))
            #         else:
            #             reqNameMap[reqText].append('No name used')

    # descend element tree
    for childElement in element:
        if childElement.tag in tagsWithTextChildren:
            textToAdd += getChildText(childElement, reqSet, eventSet, fileElement, indentLevel + 1)

    return textToAdd

def formatReqEvents() -> str:
    reqEventText = ''
    for req, events in reqEventMap.items():
        events.sort()
        reqEventText += f'\n\n== {req} =='

        for event in events:
            reqEventText += f'\n* {event}'
    return reqEventText

def writeToFile(fileName: str, fileText: str):
    file = open(cwd + "\\" + fileName, 'w', encoding='utf-8')
    file.write(fileText)
    file.close()

outputText = ''


for fileName in fileNames:
    outputText += f'\n\nFILE: {fileName}\n'
    # print(fileName) # see which file causes malfunction
    fileElement = ET.parse(dataPath + fileName).getroot()

    # loop over all events in file
    for childElem in fileElement:
        tag = childElem.tag
        eventName = ''
        if tag in eventTypes:
            eventName = childElem.get('name')

            reqSet = set()
            eventSet = set()
            eventText = getChildText(childElem, reqSet, eventSet, fileElement, 0)
            if len(eventText.strip()) > 0:
                outputText += f'\n\n'
                outputText += eventText

                # add to map of reqs and events
                for req in reqSet:
                    if req not in reqEventMap.keys():
                        reqEventMap.update({req : []})
                    reqEventMap[req].append(eventName)

# eliminate duplicate values
for req, names in reqNameMap.items():
    reqNameMap[req] = [*set(names)]
    reqNameMap[req].sort()

with open('blueOptionNames.json', 'w') as file:
    json.dump(reqNameMap, file, indent=4, sort_keys=True)

writeToFile('events.txt', outputText)
reqEventText = formatReqEvents()
writeToFile('blueOptions.txt', reqEventText)

# EXTRA: Regular expression to find any 'choice' element with a 'req':
# <choice.*req="
