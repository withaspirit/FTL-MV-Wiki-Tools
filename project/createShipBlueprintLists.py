import re
import blueprintUtils as blueprintUtils

# Creates blueprintLists for ships. Note that Elite and single-page ships are
# out of order in output text

# files used
# autoBlueprints.xml
# blueprints.xml
# dlcBlueprints.xml
# {shipLayout}.txt (all)

pathToData = blueprintUtils.pathToData
layoutHeading = 'Layout '

# ships where <class> does not match the corresponding wikiPage
# also includes ships with their own page
# ordered, such that first precedes second (prevents false positives for 'x in y'):
# SYLVANTRANS, SYLVAN
# PLEASUREFLAG, PLEASURE
# WITHER_2, WITHER
pageShipClassMismatch = {
    'ELITE_SHIP': 'Elite_Ships#',
    'PLAYER_SHIP_MVKESTREL': 'Multiverse Cruisers#',
    'PLAYER_SHIP_MVFED': 'Multiverse Cruisers#',
    'PLAYER_SHIP_MVSTEALTH': 'Multiverse Cruisers#',

    'PLAYER_SHIP_MVENGI': 'Multiverse Cruisers (2)#',
    'PLAYER_SHIP_MVCIVILIAN': 'Multiverse Cruisers (2)#',
    'PLAYER_SHIP_MVCRYSTAL': 'Multiverse Cruisers (2)#',

    'PLAYER_SHIP_MVDYNASTY': 'Multiverse Cruisers (3)#',
    'PLAYER_SHIP_MVLANIUS': 'Multiverse Cruisers (3)#',
    'PLAYER_SHIP_FLAGSHIP': 'Multiverse Flagship (player)#',
    'PLAYER_SHIP_PROTOMV': 'Prototype-Multiverse Cruisers#',
    'PLAYER_SHIP_MFK': 'MFK Cruisers#',
    'PLAYER_SHIP_ANGEL': 'Angel Cruisers#',
    'PLAYER_SHIP_SPIDER': 'Spider Hunter Cruisers#',
    'PLAYER_SHIP_SYLVAN_TRANSPORT': 'Merchant Transport#',
    'PLAYER_SHIP_SYLVAN': 'Sylvan Cruisers#',
    'PLAYER_SHIP_MORPH': 'Morph Spurgle Yurgle#',
    'PLAYER_SHIP_HEKTAR': 'Hektar Cruisers#',
    'PLAYER_SHIP_PLEASUREFLAG': 'Pleasure Flagship',
    'PLAYER_SHIP_PLEASURE': 'Slug Pleasure Barges#',
    'CREW_SHIP_SLOT1': 'Slot 1 Crewsers#',
    'CREW_SHIP_SLOT2': 'Slot 2 Crewsers#',
    'CREW_SHIP_SLOT3': 'Slot 3 Crewsers#',
    'CREW_SHIP_SLOT4': 'Slot 4 Crewsers#',
    'CREW_SHIP_SLOT5': 'Slot 5 Crewsers#',
    'CREW_SHIP_SLOT6': 'Slot 6 Crewsers#',
    'CREW_SHIP_SLOT7': 'Slot 7 Crewsers#',
    'CREW_SHIP_SLOT8': 'Slot 8 Crewsers#',
    'CREW_SHIP_SLOTA': 'Slot A Crewsers#',
    'CREW_SHIP_SLOTB': 'Slot B Crewsers#',
    'CREW_SHIP_WITHER_2': 'Orchid Children Crewser',
    'CREW_SHIP_WITHER': "Aenwithe's Crewser",
    'CREW_SHIP_ORCHID': 'Orchid Crewsers#',
    'CREW_SHIP_ORCHID_2': 'Orchid Crewsers#',
    'CREW_SHIP_ORCHID_3': 'Orchid Crewsers#',
    'VANILLA_SHIP_FED': 'Vanilla Federation Cruisers#',
    'PLAYER_SHIP_PONY': 'Equinoid Cruisers#',
    'PLAYER_SHIP_VANILLA': 'Alpha Kestrel Cruiser',
    'PLAYER_SHIP_LIMIT_4': 'Unoptimized Cruiser MK IV'
}

singleShips = {
    'CREW_SHIP_WITHER_2': 'Orchid Children Crewser',
    'CREW_SHIP_WITHER': "Aenwithe's Crewser",
    'PLAYER_SHIP_VANILLA': 'Alpha Kestrel Cruiser',
    'PLAYER_SHIP_PLEASUREFLAG': 'Pleasure Flagship',
    'PLAYER_SHIP_LIMIT_4': 'Unoptimized Cruiser MK IV'
}

def getShipText():
    blueprints = blueprintUtils.getBlueprints()

    shipPath = './/shipBlueprint'
    shipBlueprints = blueprints.findall(shipPath)
    wikiPageShipMap = buildWikiPageShipMap(shipBlueprints)

    shipText = ''
    for wikiPageName, shipNames in wikiPageShipMap.items():
        wikiListName = getWikiListName(shipNames[0])

        #print(f'{wikiPageName}: more than one ship: {pageHasMoreThanOneShip}')
        if len(shipNames) > 1 and (wikiPageName[-1] != '#'):
            wikiPageName += '#'

        shipText += f'''
        <!--
            {wikiPageName}
            https://ftlmultiverse.fandom.com/wiki/{wikiPageName.replace(' ', '_')}
        -->
            <blueprintList wikiPage="{wikiPageName}" name="LIST_SHIPS_{wikiListName}_WIKI">'''

        for blueprintName in shipNames:
            shipBlueprintPath = f'.//shipBlueprint[@name="{blueprintName}"]'
            shipBlueprint = blueprints.find(shipBlueprintPath)

            shipClass = shipBlueprint.find('class').text
            wikiHeading = getWikiHeadingShip(blueprintName, shipClass, wikiPageName)
            wikiName = getWikiNameShip(blueprintName, shipClass, wikiPageName, wikiHeading)
            teleporterLimit = getTeleporterLimit(shipBlueprint)

            if (blueprintName == 'PLAYER_SHIP_LIMIT_4'):
                wikiName = wikiName.replace('Mk', 'MK')
                wikiHeading = wikiHeading.replace('Mk', 'MK')

            shipText += f'''
                <name wikiName="{wikiName}" wikiHeading="{wikiHeading}" teleporterLimit="{teleporterLimit}">{blueprintName}</name>'''

        shipText +=  f'''
            </blueprintList>\n'''

    shipText = blueprintUtils.processText(shipText)
    return shipText

def buildWikiPageShipMap(shipBlueprints) -> dict[str, list[str]]:
    wikiPageShipMap = {}

    for shipBlueprint in shipBlueprints:
        blueprintName = shipBlueprint.get('name')
        wikiPageName = shipBlueprint.find('class').text # assume every ship has a class

        # technically inefficient way to pluralize common ships
        if 'Cruiser' or 'Bomber' in wikiPageName:
            wikiPageName = wikiPageName.replace('Bomber', 'Bombers')
            wikiPageName = wikiPageName.replace('Cruiser', 'Cruisers')
            wikiPageName += '#'

        # get page for ships with wikiPage not matching <class> -> overrides pluralized versions
        for shortenedBlueprintName, wikiPage in pageShipClassMismatch.items():
            if shortenedBlueprintName in blueprintName:
                wikiPageName = wikiPage
                break

        if wikiPageName not in wikiPageShipMap:
            pageNameShipList = {wikiPageName : []}
            wikiPageShipMap.update(pageNameShipList)
        wikiPageShipMap[wikiPageName].append(blueprintName)

    return wikiPageShipMap

# help create the 'name' attribute for blueprintList
# format: LIST_SHIPS_<name>_WIKI
# have to use this because MV Rebel Cruiser does not use 'Multiverse' in its name
wikiListNameMap = {
    'PLAYER_SHIP_MVKESTREL': 'MV',
    'PLAYER_SHIP_MVFED': 'MV',
    'PLAYER_SHIP_MVSTEALTH': 'MV',

    'PLAYER_SHIP_MVENGI': 'MV_2',
    'PLAYER_SHIP_MVCIVILIAN': 'MV_2',
    'PLAYER_SHIP_MVCRYSTAL': 'MV_2',

    'PLAYER_SHIP_MVDYNASTY': 'MV_3',
    'PLAYER_SHIP_MVLANIUS': 'MV_3'
}

# get 'name' attribute used for blueprintLists
def getWikiListName(blueprintName):
    wikiListName = ''
    if blueprintName in wikiListNameMap:
        wikiListName = wikiListNameMap[blueprintName]
    elif 'PLAYER_SHIP' in blueprintName:
        wikiListName = blueprintName.replace('PLAYER_SHIP_', '')
    elif ('VANILLA' in blueprintName) or ('CREW' in blueprintName):
        wikiListName = blueprintName.replace('_SHIP', '')
    elif 'ELITE' in blueprintName:
        wikiListName = 'ELITE'
    return wikiListName

def getWikiNameShip(blueprintName: str, shipClass: str, wikiPageName: str, wikiHeading: str) -> str:
    wikiName = ''

    if blueprintName in wikiListNameMap:
        wikiName = shipClass
    elif 'Multiverse' in wikiPageName:
        # proto-mv, multiverse flagship
        layoutLetter = wikiHeading.replace(layoutHeading, '')
        wikiName = f'{shipClass} {layoutLetter}'
    elif layoutHeading in wikiHeading:
        # -2 to get rid of 's#'
        lastTwoChars = wikiPageName[-2:]
        layoutLetter = wikiHeading.replace(layoutHeading, '')
        if lastTwoChars == 's#':
            wikiName = f'{wikiPageName[:-2]} {layoutLetter}'
        else:
            # ex: for 'Morph Spurgle Yurgle#Layout A'
            wikiName = f'{wikiPageName[:-1]} {layoutLetter}'
    else:
        wikiName = wikiHeading
    return wikiName

def getWikiHeadingShip(blueprintName: str, shipClass: str, wikiPageName: str) -> str:
    wikiHeading = ''

    if wikiPageName[-1] != '#':
        # single-page ships
        wikiHeading = shipClass
    elif ('CREW' in blueprintName) or ('ELITE' in blueprintName):
        if 'Crewser' in shipClass:
            shipClass = shipClass.replace('Crewser', 'Cruiser')
        wikiHeading = shipClass
    elif blueprintName in wikiListNameMap:
        shipClassCorrect = shipClass.replace('MV ', '')
        shipClassCorrect = shipClassCorrect.replace('Cruiser', '')
        shipClassCorrect += 'Multiverse Cruiser'
        wikiHeading = shipClassCorrect
    else:
        layoutId = getLayoutId(blueprintName)
        wikiHeading = f'{layoutHeading}{layoutId}'
    return wikiHeading

def getLayoutId(blueprintName):
    layoutId = ''
    lastTwoChars = blueprintName[len(blueprintName) - 2 : len(blueprintName)]
    if '_2' == lastTwoChars:
        layoutId = 'B'
    elif '_3' == lastTwoChars:
        layoutId = 'C'
    else:
        layoutId = 'A'
    return layoutId

# get teleporter room size
def getTeleporterLimit(blueprint) -> int:
    layout = blueprint.get('layout')
    layoutFileName = layout.replace(' ', '_') + '.txt'
    layoutFile = open(pathToData + layoutFileName, 'r')
    fileText = layoutFile.read()

    systemList = blueprint.find('systemList')
    # assume that all ships include a room supporting a teleporter
    teleporter = systemList.find('teleporter')
    if teleporter is None:
        return 0

    teleRoomNumber = teleporter.get('room')
    roomRegex = f'ROOM\n{teleRoomNumber}\n-?\d+\n-?\d+\n(-?\d+)\n(-?\d+)'
    regexp = re.compile(roomRegex)
    match = regexp.search(fileText)

    if match:
        roomLength = int(match.group(1))
        roomWidth = int(match.group(2))
        roomArea = roomLength * roomWidth

        if roomArea <= 0:
            raise Exception('Groups not captured properly')
        return roomArea
    return -1

# main section
if __name__ == '__main__':
    getShipText = getShipText()
    print(getShipText)
