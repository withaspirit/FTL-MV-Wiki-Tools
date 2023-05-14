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
# have THE FTL DAT file in this folder
dataDir = 'FTL DAT\\data\\'
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
    # "events_mantis.xml.append", # not well formed
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

eventTypes = {
    'event',
    'eventList'
}

tagsWithTextChildren = {
    'event',
    'choice',
    'eventList'
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


# blue options
reqEventMap = {}
reqNameMap = {}

dummyElement = ET.Element('dummy')

def findElementByName(fileElement : ET.Element, tag : str, name : str):
    if fileElement == dummyElement:
        # search for element in files
        # TODO: look into index for easier access
        for fileName in fileNames:
            newFileElement = ET.parse(dataPath + fileName).getroot()
            elems = newFileElement.findall(f".//{tag}[@name='{name}']")
            if len(elems) > 0:
                # return last version of element
                return elems[len(elems) - 1]
    else:
        elems = fileElement.findall(f".//{tag}[@name='{name}']")
        if len(elems) > 0:
            # return last version of element
            return elems[len(elems) - 1]
    return None

indent = '*'
# indent level is 0 by default
# get the 'text' element from every event, choice, or eventList within an eventType
parenthesizedTextRegexp = re.compile('(?<=\()(.*?)(?=\))') # text between brackets
def getChildText(element : ET.Element, reqSet : set, fileElement : ET.Element, indentLevel : int = 0) -> str:
    textToAdd = ''

    textElem = element.find('text')
    textElemText = ''
    if textElem is not None:
        if textElem.text is not None:
            # append text with indent
            textElemText = textElem.text
            textToAdd += '\n' + (indent * indentLevel)
            textToAdd += f"''{textElem.text}''"
        
        # textList
        loadAttr = textElem.get('load')
        if loadAttr is not None and len(loadAttr) > 0:
            textToAdd += '\n' + (indent * indentLevel)
            textToAdd += 'textList:'
            textListElem = findElementByName(fileElement, 'textList', loadAttr)
            if textListElem is None:
                textListElem = findElementByName(dummyElement, 'textList', loadAttr)

            for elem in textListElem.iter('text'):
                textToAdd += '\n' + (indent * (indentLevel + 1))
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
            textToAdd += getChildText(childElement, reqSet, fileElement, indentLevel + 1)

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
        if tag in eventTypes:
            # skip over duplicates
            # eventName = childElem.get('name')
            # eventElem = findElementByName(fileElement, tag, eventName)

            reqSet = set()
            eventText = getChildText(childElem, reqSet, fileElement)
            if len(eventText.strip()) > 0:
                outputText += f'\n\n{eventElem.tag}: {eventName}'
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
