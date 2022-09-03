import os
import blueprintUtils
from weaponExport import Weapon

# Creates Weapon Tables
# FIXME: configure to output
# (1) all weapons in one table
# (2) separate tables

# file to write to
filePath = '\wikiWeaponTables.txt'

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
    'LIST_WEAPONS_ALL_CRAPBUCKET'
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
    "Cost",
    "[[Rarity]]",
    "Speed",
    # "Other"
]

tableStyle = '''{|class="wikitable floatheader sortable" style="text-align:center;" cellspacing="0" cellpadding="0" border="1"'''

blueprints = blueprintUtils.blueprints
autoBlueprints = blueprintUtils.autoBlueprints
bpLists = autoBlueprints.findall('.//blueprintList[@wikiPage]')

text = tableStyle
rowOfColumns = "!!".join(allColumns)
text += f'|-\n!{rowOfColumns}\n'

tableList = []
allColumnsSet = set(allColumns)
# iterate over each weapon list
for blueprintList in bpLists:

    listName = blueprintList.get('name')
    # iterate over only weapon lists
    if (listName in skipNames or
        ('LIST_WEAPONS_' not in listName and listName not in otherWeaponLists)):
        continue

    #wikiPage = blueprintList.get('wikiPage')
    #tableText = f'\n\n{wikiPage}'
    tableText = '\n|-\n'

    weaponRows = []
    for nameElem in blueprintList.iter('name'):
        weaponName = nameElem.text
        weaponPath = f'.//weaponBlueprint[@name="{weaponName}"]'
        blueprint = blueprintUtils.getNormalBlueprint(weaponPath)
        weapon = Weapon(blueprint, allColumnsSet)
        weaponRows.append(weapon.toString())

    tableText += '|'
    tableText += '\n|-\n|'.join(weaponRows)
    tableList.append(tableText)
    #print(weaponList)

# end of table
text += '\n\n'.join(tableList)
text += '''\n|}\n
<small>Want to edit this table? Click [[Editing Tables|here]]</small>'''

cwd = os.path.dirname(os.path.abspath(__file__))
with open(cwd + filePath, 'w', encoding='utf-8') as file:
    file.write(text)
