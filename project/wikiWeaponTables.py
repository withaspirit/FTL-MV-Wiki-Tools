import os
import blueprintUtils
from weaponExport import Weapon
import yaml

cwd = os.path.dirname(os.path.abspath(__file__))

# pip install pyyaml

# Creates Weapon Tables:
# (1) separate tables
# (2) all weapons in one table

# blueprintLists of weapons that don't have 'LIST_WEAPONS_' in their name
otherWeaponLists = {
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

# blueprintLists of weapons with 'LIST_WEAPONS_' in their name that should be
# excluded
skipNames = {
    'LIST_WEAPONS_ARTILLERY_WIKI',
    'LIST_WEAPONS_ALL_CRAPBUCKET',
    'LIST_WEAPONS_MODULAR_MODULES_WIKI',
}

# All possible columns
allColumns = [
    "Weapon",
    "H",
    "S",
    "C",
    "I",
    "Pierce",
    "Shots",
    "Radius",
    "Length",
    "Power",
    "Cooldown",
    "Fire",
    "Breach",
    "Stun",
    "Free Missile Chance",
    "Cost",
    "[[Rarity]]",
    "Speed",
    # "Other"
]


tableStartText = '''{|class="wikitable floatheader sortable" style="text-align:center;" cellspacing="0" cellpadding="0" border="1"'''
tableEndText = '''\n|}\n
<small>Want to edit this table? Click [[Editing Tables|here]]</small>\n'''

def wrapTable(columns, tableText):
    rowOfColumns = formatColumnHeaders(columns)
    tableStart = tableStartText + f'|-\n{rowOfColumns}\n'
    tableText = tableStart + tableText + tableEndText
    return tableText

# format column header according to wiki
dmgTypeSet = {'H', 'S', 'C', 'I'}
def formatColumnHeaders(columns: list) -> str:
    # find how many of letters in dmgSet to include (colSpan)

    dmgTypeList = []
    for column in columns:
        if column in dmgTypeSet:
            dmgTypeList.append(column)

    columnList = []
    dmgSeen = False
    for column in columns:
        # skip dmgTypeSet (they go on first row)
        if column in dmgTypeSet:
            if dmgSeen == False:
                columnList.append(f'colspan="{len(dmgTypeList)}" |Damage')
                dmgSeen = True
            else:
                continue
        else:
            columnList.append(f'rowspan="2" |{column}')

    # add second row (column names)
    columnHeader = '|-\n! ' + '\n! '.join(columnList)
    # add first row (damage types)
    columnHeader += '\n|-\n!' + '\n!'.join(dmgTypeList)
    return columnHeader

def weaponTable(weaponList):
    tableText = '\n|-\n|'
    tableText += '\n|-\n|'.join(weaponList)
    return tableText

blueprints = blueprintUtils.blueprints
autoBlueprints = blueprintUtils.autoBlueprints
bpLists = autoBlueprints.findall('.//blueprintList[@wikiPage]')

columnFile = open(cwd + './utils/tableColumns.yaml', 'r')
columnMap = yaml.safe_load(columnFile)

individualTableList = []
allTableList = []

allColumnSet = set(allColumns)

# make this T/F 
completeTable = False
# iterate over each weapon list
for blueprintList in bpLists:

    listName = blueprintList.get('name')
    # iterate over only weapon lists
    if (listName in skipNames or
        ('LIST_WEAPONS_' not in listName and listName not in otherWeaponLists)):
        continue
    
    columns = columnMap[listName]
    columnSet = set(columns)

    weaponList = []
    weaponAllList = []
    for nameElem in blueprintList.iter('name'):
        blueprintName = nameElem.text

        isEnemyWeapon = blueprintName[len(blueprintName) - 6:] == '_ENEMY'
        if isEnemyWeapon:
            continue

        weaponPath = f'.//weaponBlueprint[@name="{blueprintName}"]'
        blueprint = blueprintUtils.getNormalBlueprint(weaponPath)

        weapon = Weapon(blueprint, columnSet)
        weaponList.append(weapon.toString())

        weaponAll = Weapon(blueprint, allColumnSet)
        weaponAllList.append(weaponAll.toString())

    tableText = weaponTable(weaponList)
    individualTableList.append(wrapTable(columns, tableText))

    tableAllText = weaponTable(weaponAllList)
    allTableList.append(tableAllText)

columnFile.close()

# end of table
individualTableText = '\n\n'.join(individualTableList)

allTableText = '\n\n'.join(allTableList)
allTableText = wrapTable(allColumns, allTableText)

with open(cwd + '\wikiWeaponTables.txt', 'w', encoding='utf-8') as file:
    file.write(individualTableText)

with open(cwd + '\wikiWeaponTablesAll.txt', 'w', encoding='utf-8') as file:
    file.write(allTableText)

