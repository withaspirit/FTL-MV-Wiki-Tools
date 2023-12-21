import xml.etree.ElementTree as ET
import os
import json

# current working directory
cwd = os.path.dirname(os.path.abspath(__file__)) + "\\"
# have THE FTL DAT file in this folder
dataDir = 'FTL DAT Orig\\data\\'
# create file path
dataPath = cwd + dataDir

fileNames = [
    'sector_data.xml.append'
]

eventTypes = {
    'event',
    'priorityEvent',

}

beaconTags = {
    'exitBeacon',
    'rebelBeacon',
    'quest'  # not a beacon but it has "event" attribute so it works for now
}

beaconEvents = {
    'event',
    'nebulaEvent',
    'rebelEvent',
}

# look for eventLists
# if only child of event is eventList: treat like eventList



startEvent = 'startEvent'

sectorEvents = []


for fileName in fileNames:
    # print(fileName) # see which file causes malfunction
    fileElement = ET.parse(dataPath + fileName).getroot()
     # loop over all events in file
    for elem in fileElement:
        tag = elem.tag
        if tag == 'sectorDescription':
            for childElem in elem:
                childTag = childElem.tag
                if childTag == startEvent:
                    sectorEvents.append(childElem.text)
                elif childTag in beaconTags:
                    for eventType in beaconEvents:
                        attribute = childElem.get(eventType)
                        print(attribute)
                        if attribute is not None:
                            sectorEvents.append(attribute)
                elif childTag in eventTypes:
                    sectorEvents.append(childElem.get('name'))

with open('utils/sectorEvents.json', 'w') as file:
    json.dump(list(dict.fromkeys(sectorEvents)), file, indent=4)

# sectorDescription
