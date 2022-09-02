import blueprintUtils as blueprintUtils

# https://ftlmultiverse.fandom.com/wiki/Weapon_Tables

accuracyImages = {
    '10': '',
    '20': '',
    '30': '{{Accuracy|30}}',
}

tableThing = '''{|class=" wikitable floatheader sortable" style="text-align:center;" cellspacing="0" cellpadding="0" border="1"
|-'''

columnFormats = {
    'weapon': '! rowspan="2" |Weapon',
    'damagehsc': '! colspan="3" |Damage',
    'damagehsci': '! colspan="4" |Damage',
    'shots': '! rowspan="2" |Shots',
    'power': '! rowspan="2" |Power',
    'pierce': '! rowspan="2" |Piercing',
    'effects': '''! rowspan="2" |Fire
! rowspan="2" |Breach
! rowspan="2" |Stun''',
    'misc': '''! rowspan="2" |Cost
! rowspan="2" |[[Rarity]]
! rowspan="2" |Speed''',
    'hsc': '''|-
!H
!S
!C''',
    'hsci': '''|-
!H
!S
!C
!I'''
}


# IDEA: for missiles: [shot]/1{{Missiles}}
defaults = {
    'persDamage': 1, # x15
    'sysDamage': 1,
    'stun': 3,
    'stunChance': 100
}

icons = {
    'rad': '{{RadDebuffIcon}}',
    'scrap': '{{Scrap}}'
}

class Weapon:
    
    validColumns = {}

    columnValues = None

    def __init__(self, blueprint, validColumns):
        self.blueprint = blueprint
        self.blueprintName = self.blueprint.get('name')
        self.validColumns = validColumns
        self.columnValues = []


# SPECIAL COLUMNS
# EVENT_WEAPONS: faction column
# 
# CLONE_CANNON: crew
# 
# SKIP: if _ENEMY in name
# special effects:
# ZOLTAN_DELETER
# SALT_LAUNCHER
# skip clone cannon, separate table? 

    def getWeapon(self):
        link = self.getWikiLink()
        img = self.getImg()
        columnText = f'{link}<br>[[File:{img}.png]]'

        self.columnValues.append(columnText)

    def getWikiLink(self) -> str:
        return self.blueprint.find('.//wikiLink').text

    def getImg(self) -> str:
        return self.blueprint.find('.//weaponArt').text

    def getHullDamage(self):
        if 'H' not in self.validColumns:
            return

        columnText = self.getElementText('damage')
        self.columnValues.append(columnText)

    def getSysDamage(self) -> str:
        if 'S' not in self.validColumns:
            return ''

        columnText = self.getElementText('sysDamage')
        self.columnValues.append(columnText)

    def getCrewDamage(self) -> str:
        if 'C' not in self.validColumns:
            return ''
        
        columnText = self.getElementText('persDamage')
        self.columnValues.append(columnText)

    def getIonDamage(self) -> str:
        if 'I' not in self.validColumns:
            return ''
        
        columnText = self.getElementText('ion')
        self.columnValues.append(columnText)
    
    def getShots(self) -> str:
        columnText = self.getElementText('shots')
        self.columnValues.append(columnText)

    def getRadius(self) -> str:
        columnText = self.getElementText('radius')
        self.columnValues.append(columnText)

    def getLength(self) -> str:
        columnText = self.getElementText('length')
        self.columnValues.append(columnText)

    def getPower(self) -> str:
        columnText = self.getElementText('power')
        self.columnValues.append(columnText)

    def getPierce(self) -> str:
        columnText = self.getElementText('sp')
        self.columnValues.append(columnText)
    
    def getCooldown(self) -> str:
        columnText = self.getElementText('cooldown')
        self.columnValues.append(columnText)

    def getFireChance(self) -> str:
        columnText = self.getElementText('fireChance')
        self.columnValues.append(columnText)

    def getBreachChance(self) -> str:
        columnText = self.getElementText('breachChance')
        self.columnValues.append(columnText)

    def getStun(self) -> str:
        stunChanceElem = self.blueprint.find('stunChance')
        stunElem = self.blueprint.find('stun')

        columnText = ' ! '
        if stunChanceElem is None and stunElem is None:
            return columnText

        if stunChanceElem is None:
            columnText += '100% '
        else:
            columnText += f'{stunChanceElem.text}% '

        if stunElem is None:
            columnText = '(3s)'
        else:
            columnText = f'({stunElem.text}s)'

        return columnText

    def getCost(self) -> str:
        columnText = self.getElementText('cost')
        if len(columnText) == 0:
            columnText = '0'

        columnText += icons["scrap"]
        self.columnValues.append(columnText)

    def getRarity(self) -> str:
        columnText = self.getElementText('rarity')
        self.columnValues.append(columnText)

    def getSpeed(self) -> str:
        columnText = self.getElementText('speed')
        self.columnValues.append(columnText)

    def getElementText(self, tag: str) -> str:
        elem = self.blueprint.find(tag)
        if elem is None:
            return ''
        return elem.text