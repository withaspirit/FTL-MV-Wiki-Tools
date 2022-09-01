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

    def __init__(self, blueprint, validColumns):
        self.blueprint = blueprint
        self.blueprintName = self.blueprint.get('name')
        self.validColumns = validColumns

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
        return f'\n|{link}<br>[[File:{img}.png]]'

    def getWikiLink(self) -> str:
        return self.blueprint.find('.//wikiLink').text

    def getImg(self) -> str:
        return self.blueprint.find('.//weaponArt').text

    def getHullDamage(self) -> str:
        if self.validColumns['H'] is False:
            return ''

        damageElem = self.blueprint.find('damage')
        if damageElem is None:
            return ''

        return damageElem.text
        
    def getSysDamage(self) -> str:
        if self.validColumns['S'] is False:
            return ''

        sysdamageElem = self.blueprint.find('sysDamage')
        if sysdamageElem is None:
            return ''
        return sysdamageElem.text

    def getCrewDamage(self) -> str:
        if self.validColumns['C'] is False:
            return ''
        
        crewdamageElem = self.blueprint.find('persDamage')
        if crewdamageElem is None:
            return ''
        return crewdamageElem.text

    def getIonDamage(self) -> str:
        if self.validColumns['I'] is False:
            return ''
        
        ionDamageElem = self.blueprint.find('ion')
        if ionDamageElem is None:
            return ''
        return ionDamageElem.text
    
    def getShots(self) -> str:
        shotsElem = self.blueprint.find('shots')

        columnText = ' ! '
        if shotsElem is not None:
            columnText += shotsElem.text
        return columnText

    def getRadius(self) -> str:
        radiusElem = self.blueprint.find('radius')

        columnText = ' ! '
        if radiusElem is not None:
            columnText += radiusElem.text
        return columnText

    def getLength(self) -> str:
        lengthElem = self.blueprint.find('length')

        columnText = ' ! '
        if lengthElem is not None:
            columnText += lengthElem.text
        return columnText

    def getPower(self) -> str:
        powerElem = self.blueprint.find('power')

        columnText = ' ! '
        if powerElem is not None:
            columnText += powerElem.text
        return columnText

    def getPierce(self) -> str:
        pierceElem = self.blueprint.find('sp')

        columnText = ' ! '
        if pierceElem is not None:
            columnText += pierceElem.text
        return columnText
    
    def getFireChance(self) -> str:
        cooldownElem = self.blueprint.find('cooldown')

        columnText = ' ! '
        if cooldownElem is not None:
            columnText += cooldownElem.text
        return columnText

    def getFireChance(self) -> str:
        fireElem = self.blueprint.find('fireChance')

        columnText = ' ! '
        if fireElem is not None:
            columnText += f'{fireElem.text}%'
        return columnText

    def getBreachChance(self) -> str:
        breachElem = self.blueprint.find('breachChance')

        columnText = ' ! '
        if breachElem is not None:
            columnText += f'{breachElem.text}%'
        return columnText

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
        costElem = self.blueprint.find('cost')

        columnText = ' ! '
        if costElem is None:
            return columnText + '0'
        else:
            columnText += f'{costElem}{icons["scrap"]}'
        return columnText

    def getSpeed(self) -> str:
        rarityElem = self.blueprint.find('rarity')

        columnText = ' ! '
        if rarityElem is not None:
            columnText += rarityElem.text
        return columnText

    def getSpeed(self) -> str:
        speedElem = self.blueprint.find('speed')

        columnText = ' ! '
        if speedElem is not None:
            columnText += speedElem.text
        return columnText
