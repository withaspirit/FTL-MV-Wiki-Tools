import json

# run after running `parseAllEvents.py` to get the frequency of each event

eventTypes = {
    'event',
    'eventList'
}

eventCounter = dict()

with open('events.txt', 'r', errors='ignore') as eventsFile:
    lines = eventsFile.readlines()

    for row in lines:
        for eventType in eventTypes:
            eventIdentifier = f'{eventType}: '
            if eventIdentifier in row:
                cleanText = row.replace('*', '').replace('load ', '').replace(eventIdentifier, '').replace('\n', '')
                if cleanText not in eventCounter.keys():
                    eventCounter[cleanText] = 0
                eventCounter.update({cleanText : eventCounter[cleanText] + 1})

with open('utils/eventFrequency.json', 'w') as eventFrequency:
    sortedDict = dict(sorted(eventCounter.items(), key = lambda item : item[1], reverse=True))
    eventFrequencyJson = json.dumps(sortedDict, indent=4)
    eventFrequency.write(eventFrequencyJson)
