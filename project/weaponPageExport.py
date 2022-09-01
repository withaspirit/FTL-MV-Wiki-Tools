import xml.etree.ElementTree as ET
import os
import blueprintUtils as blueprintUtils

# TODO: add "type" var to bpLists to distinguish between weaponLists,
# droneLists, artilleryLists, augmentLists, shipLists etc.

# weaponPageExport limited atm to Starting Weapons

# weaponLists that are in the autoBlueprints.xml instead of the
# autoBlueprints.xml.append file
otherWeaponLists = {
    'GIFTLIST_KERNEL',
    'GIFTLIST_KERNEL_ELITE',
    'GIFTLIST_RUSTY',
    'SHOP_ITEM_SYLVAN_CONSERVATIVE',
    'BLUELIST_WEAPONS_RECYCLER',
    'HEKTAR_MODULAR_LASERS',
    'HEKTAR_MODULAR_BEAMS',
    'HEKTAR_MODULAR_MISSILES',
    'HEKTAR_MODULAR_IONS',
    'GIFTLIST_SPORE',
    'LIST_WEAPONS_NEWGEN',
    'JUDGELIST_ROCK_MATH_LOOT',
    'JUDGELIST_ROCK_RENEGADE_LOOT',
}

skipNames = {
    'LIST_WEAPONS_ARTILLERY_WIKI',
    'LIST_WEAPONS_ALL_CRAPBUCKET'
}

shipsToSkip = {
    'PLAYER_SHIP_PALADIN',
    'PLAYER_SHIP_PALADIN_2',
    'PLAYER_SHIP_PALADIN_3',
    'PLAYER_SHIP_GUARD',
    'PLAYER_SHIP_GUARD_2',
    'PLAYER_SHIP_GUARD_3',
    'PLAYER_SHIP_VAMPWEED',
    'PLAYER_SHIP_VAMPWEED_2'
}

blueprints = blueprintUtils.blueprints
autoBlueprints = blueprintUtils.autoBlueprints
bpLists = autoBlueprints.findall('.//blueprintList[@wikiPage]')

# build map of starting weapons to ships they're on
# weaponTitle: {shipWikiLink, count}
def buildStartingWeaponMap():
    weaponShipMap = {}
    for blueprintList in bpLists:

        # skip invalid cases
        listName = blueprintList.get('name')
        if listName in skipNames:
            continue

        # include only weapon lists
        if 'LIST_WEAPONS_' not in listName and listName not in otherWeaponLists:
            continue

        # weaponTitle
        for nameElem in blueprintList.iter('name'):
            weaponName = nameElem.text
            weaponShipMap[weaponName] = {}

            weaponPath = f'weaponList/weapon[@name="{weaponName}"]'

            # each 2 dots traverses back up tree once
            shipWithWeaponPath = f'.//shipBlueprint/{weaponPath}....'
            for shipElem in blueprints.findall(shipWithWeaponPath):

                shipName = shipElem.get('name')
                if shipName in shipsToSkip:
                    continue

                # {shipLink, count}
                weaponCount = len(shipElem.findall(f'.//{weaponPath}'))
                shipLink = shipElem.find('wikiLink').text
                weaponShipMap[weaponName][shipLink] = weaponCount
    return weaponShipMap

def getStartingWeapons(weaponName: str) -> str:
    text = '\n* Starting weapon on:'
    for (shipLink, count) in weaponShipMap[weaponName].items():
        text += f'\n** {shipLink}'

        if int(count) > 1:
            text += f' x{count}'
    return text

weaponShipMap = buildStartingWeaponMap()

text = ''
for blueprintList in bpLists:

    listName = blueprintList.get('name')
    if listName in skipNames:
        continue

    # include only weapon lists
    if 'LIST_WEAPONS_' not in listName and listName not in otherWeaponLists:
        continue

    # fullURL
    wikiPage = blueprintList.get("wikiPage").replace(" ", "_")
    fullURL = f'https://ftlmultiverse.fandom.com/wiki/{wikiPage}'
    text += f'\n\n\n{fullURL}\n'

    for nameElem in blueprintList.iter('name'):
        weaponName = nameElem.text
        if weaponName not in weaponShipMap or len(weaponShipMap[weaponName]) == 0:
            continue

        weaponTitlePath = f'.//weaponBlueprint[@name="{weaponName}"]/wikiName'
        weaponTitle = blueprintUtils.getNormalBlueprint(weaponTitlePath).text
        text += f'\n\n{weaponTitle}'
        text += getStartingWeapons(weaponName)

cwd = os.path.dirname(os.path.abspath(__file__))
with open(cwd + '\wikiWeaponPages.txt', 'w', encoding='utf-8') as file:
    file.write(text)
