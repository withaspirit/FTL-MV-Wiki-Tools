import blueprintUtils as blueprintUtils
import time
from shipExport import Ship

# Gathers the text from using shipExport.Ship.toString() for every player ship.
# Writes the resulting text to a file.

# omit for 5.3
errorShips = {
    'PLAYER_SHIP_VAMPWEED',
    'PLAYER_SHIP_VAMPWEED_2'
}

def getWikiShipText() -> str:
    blueprints = blueprintUtils.getBlueprints()
    shipPath = './/shipBlueprint[@name]'
    shipBlueprints = blueprints.findall(shipPath)

    prevWikiPage = None
    currWikiPage = ''
    wikiShipText = ''
    for shipBlueprint in shipBlueprints:
        blueprintName = shipBlueprint.get('name')
        
        if blueprintName in errorShips:
            #print(f'Skipped {blueprintName}')
            continue
        
        currWikiPage = shipBlueprint.find('wikiPage').text
        if currWikiPage != prevWikiPage:
            prevWikiPage = currWikiPage
            wikiShipText += f'\n{currWikiPage}\n'

        #print(blueprintName)
        ship = Ship(shipBlueprint, blueprints)
        wikiShipText += ship.toString() + '\n'
    return wikiShipText

if __name__ == '__main__':
    start_time = time.time()

    print('Exporting player ships to Wiki format. Please wait ~30 seconds.')
    
    text = getWikiShipText()
    wikiShipsFile = open(blueprintUtils.cwd + '\wikiShips.txt', 'w', encoding='utf-8')
    wikiShipsFile.write(text)
    wikiShipsFile.close()

    print('Finished exporting ships')
    print('--- %s seconds ---' % (time.time() - start_time))
