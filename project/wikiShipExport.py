import xml.etree.ElementTree as ET
import blueprintUtils as blueprintUtils
import time
from shipExport import Ship

def getWikiShipText() -> str:
    blueprints = blueprintUtils.getBlueprints()
    shipIdentifier = './/shipBlueprint[@name]'
    shipBlueprints = blueprints.findall(shipIdentifier)

    prevWikiPage = ''
    currWikiPage = '.'
    text = ''
    shipBlueprintNames = []
    for shipBlueprint in shipBlueprints:
        blueprintName = shipBlueprint.get('name')
        currWikiPage = shipBlueprint.find('wikiPage').text

        if currWikiPage != prevWikiPage:
            prevWikiPage = currWikiPage
            text += f'\n{currWikiPage}\n'

        shipBlueprintNames.append(blueprintName)
        #print(blueprintName)
        ship = Ship(shipBlueprint, blueprints)
        text += ship.toString() + '\n'
    return text

if __name__ == '__main__':
    start_time = time.time()

    print('Beginning ship export. Please wait ~25 seconds')
    # only works for Player ships so far
    
    text = getWikiShipText()
    wikiShipsFile = open(blueprintUtils.cwd + '\wikiShips.txt', 'w', encoding='utf-8')
    wikiShipsFile.write(text)
    wikiShipsFile.close()

    print('Finished exporting ships')
    print('--- %s seconds ---' % (time.time() - start_time))
