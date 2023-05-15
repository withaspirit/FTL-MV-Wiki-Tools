import xml.etree.ElementTree as ET
import os
import re
import json

# runtime: 1 second

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
    "events_socialize.xml", # unnecessary
    "events_spider.xml",
    "events_standard.xml",
    "events_storage.xml",
    "events_transports.xml",
    "events_trapper.xml",
    "events_zoltan.xml.append",
    "newEvents.xml.append"
]

eventTypes = {
    'event',
    'eventList',
    'textList'
}

eventLocationDict = {}

for fileName in fileNames:
    # print(fileName) # see which file causes malfunction
    fileElement = ET.parse(dataPath + fileName).getroot()

    for childElem in fileElement:
        tag = childElem.tag
        if tag in eventTypes:
            eventName = childElem.get('name')
            if eventName not in eventLocationDict.keys():
                eventLocationDict[eventName] = []       
            eventLocationDict[eventName].append(fileName)

for event, locations in eventLocationDict.items():
    eventLocationDict[event] = [*set(locations)]
    eventLocationDict[event].sort()

with open('utils\\eventNameIndex.json', 'w') as eventIndexFile:
    json.dump(eventLocationDict, eventIndexFile, indent=2)
