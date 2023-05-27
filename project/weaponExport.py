import xml.etree.ElementTree as ET
import math

# https://ftlmultiverse.fandom.com/wiki/Weapon_Tables

# template: https://ftlmultiverse.fandom.com/wiki/Template:Accuracy


# unused templates: https://ftlmultiverse.fandom.com/wiki/User:Puporongo/Sandbox

icons = {
    'rad': '{{RadDebuffIcon}}',
    'scrap': '{{Scrap}}',
    'missile': '{{Missile}}',
    'accuracy': '{{Accuracy|num}}',
    'lockdown': '{{Lockdown}}',
    'non_drone_targetable': '{{NonDroneTargetable}}',
    'hullbust': '{{HullBust}}',
    # 'freemissile': '{{FreeMissileChance|{0}}}'
}

# Damage
damageAbbr = (
    '<abbr title="Increases by {2:g} after each '
    'volley, up to {1:g} after {3} volleys.">{0:g}-{1:g}</abbr>'
)
infiniteAbbr = (
    '<abbr title="Increases by {1:g} per volley, infinitely.">{0:g}-∞</abbr>'
)
# Cooldown
cooldownAbbr = (
    '<abbr title="Decreases by {2:g}s after each '
    'volley, down to {1:g}s after {3} volleys.">{0:g}-{1:g}</abbr>'
)
preemptAbbr = '<abbr title="Can only be fired once per fight.">{0:g}</abbr>'
fireTimeAbbr = '<abbr title="Fires projectiles {0:g}s apart.">{0:g}</abbr>'
startChargedAbbr = '<abbr title="Starts charged">0</abbr>'
phaserAbbrText = "Pierces 10 shield layers, ionizing the system it hits, as well as shields"
phaserAbbr = '<abbr title="Pierces 10 shield layers, ionizing the system it hits, as well as shields.">{0:g}</abbr>'

defaultSpeeds = {
    'MISSILES': '35',
    'LASER': '60',
    'BURST': '60',
    'BEAM': '5'
}

factionWeapons = {
    'LOOT_CIVILIAN_1' : 'Civilian',
    'LOOT_MILITIA_1' : 'Militia',
    'LOOT_FEDERATION_1' : 'Federation',
    'LOOT_COALITION_1' : 'Coalition',
    'LOOT_DUSKBRINGER_1' : 'Free Mantis',
    'LOOT_FREEMANTIS_1' : 'Duskbringers',
    'LOOT_LOSTSUN_1' : 'Lost Suns',
    'LOOT_LOSTSUN_2' : 'Lost Suns',
    'LOOT_MANTIS_1' : 'Hive Mantis',
    'LOOT_MANTIS_2' : 'Hive Mantis',
    'LOOT_REBEL_1' : 'Rebellion',
    'LOOT_ROCK_1' : 'Rock',
    'LOOT_ZOLTAN_1' : 'Zoltan',
    'LOOT_ZOLTAN_2' : 'Zoltan',
    'LOOT_SLUG_1' : 'Slug',
    'LOOT_CLAN_1' : 'Clan',
    'LOOT_KNIGHT_1' : 'Knight',
    'LOOT_SHELL_1' : 'Shell',
    'LOOT_LEECH_1' : 'Leech',
    'LOOT_CULTIST_1' : 'Cultist',
    'LOOT_DYNASTY_1' : 'Dynasty',
    'LOOT_LANIUS_1' : 'Lanius',
}

class Weapon:

    validColumns = {}

    columnValues = None

    def __init__(self, blueprint: ET.ElementTree, validColumns: list = []):
        self.blueprint = blueprint
        self.blueprintName = self.blueprint.get('name')
        self.validColumns = validColumns
        self.columnValues = []

    def toString(self) -> str:
        self.getWeapon()
        self.getFaction()
        self.getHullDamage()
        self.getSysDamage()
        self.getCrewDamage()
        self.getIonDamage()
        self.getPierce()
        self.getShots()
        self.getLength()
        self.getRadius()
        self.getPower()
        self.getCooldown()
        self.getFireChance()
        self.getBreachChance()
        self.getStun()
        self.getFreeMissileChance()
        self.getCost()
        self.getRarity()
        self.getSpeed()
        self.getEffects()

        return '\n| '.join(self.columnValues)

    def getWeapon(self):
        link = self.getWikiLink()
        img = self.getImg()
        columnText = f'{link}<br>[[File:{img}'
        if self.blueprintName == 'ION_PIERCE_DISCO':
            columnText += '.gif]]'
        else:
            columnText += '.png]]'

        self.columnValues.append(columnText)

    def getWikiLink(self) -> str:
        return self.blueprint.find('.//wikiLink').text

    def getImg(self) -> str:
        return self.blueprint.find('.//weaponArt').text
    
    def getFaction(self) -> str:
        if 'Faction' not in self.validColumns:
            return
        columnText = factionWeapons[self.blueprintName]
        self.columnValues.append(columnText)
        return columnText

    def getHullDamage(self) -> str:
        if 'H' not in self.validColumns:
            return

        columnText = self.getElementText('damage')
        if columnText in self.invalidSysDamageValues:
            columnText = ''
        elif len(columnText) > 0:
            damage = float(columnText)
            columnText = self.getBoost(columnText, damageAbbr, damage)

        # MODULAR_ION_HULL treats hullBusting differently
        if self.getElementText('hullBust') == '1' or 'MODULAR_ION_HULL' in self.blueprintName:
            columnText += f' {icons["hullbust"]}'

        self.columnValues.append(columnText)
        return columnText

    invalidSysDamageValues = {'0', '-1'}

    def getSysDamage(self) -> str:
        if 'S' not in self.validColumns:
            return

        columnText = self.getDamagePlusXDamage('sysDamage')

        lockdownText = self.getElementText('lockdown')
        if lockdownText == '1':
            columnText += f' {icons["lockdown"]}'

        self.columnValues.append(columnText)
        return columnText

    radStatBoosts = ['moveSpeedMultiplier', 'stunMultiplier', 'repairSpeed']
    def getCrewDamage(self) -> str:
        if ('C' not in self.validColumns):
            return

        columnText = self.getDamagePlusXDamage('persDamage')
        # get RAD Debuff if necessary
        columnText += self.getRadDebuff()
        self.columnValues.append(columnText)
        return columnText        

    # Returns rad debuff icon if rad effects present, empty str otherwise
    def getRadDebuff(self) -> str:
        appendText = ''
        statBoostsElem = self.blueprint.find('statBoosts')
        radBoostCount = 0
        if statBoostsElem is not None:

            for statBoostElem in statBoostsElem.findall('statBoost'):
                if statBoostElem.get('name') not in self.radStatBoosts:
                    radBoostCount = 0
                    break
                else:
                    radBoostCount += 1

        if radBoostCount == 3:
            appendText = icons['rad']
        return appendText


    damageDisablers = {
        'sysDamage': 'noSysDamage',
        'persDamage': 'noPersDamage',
        'ion': 'noIonDamage' # not in game but for "ion" to use the below fxn
    }
    # Adds hull damage to xDamage text
    def getDamagePlusXDamage(self, damageType: str) -> str:
        columnText = ''
        xDamageText = self.getElementText(damageType)
        noXDamage = self.damageDisablers[damageType]

        if (xDamageText in self.invalidSysDamageValues or
            self.getElementText(noXDamage) == 'true'):
            return columnText
        
        if len(xDamageText) > 0 and int(xDamageText) < -1:
            # NOTE: hacky solution for negative persDamage on BOMB_HEAL, but it works for now
            if (self.blueprintName != 'BOMB_HEAL'):
                return xDamageText
            
        isCrewDamage = False
        if damageType == 'persDamage':
            isCrewDamage = True
            if len(xDamageText) > 0:
                xDamageText = str(int(xDamageText) * 15)
        
        columnText = ''
        totalXDamage = 0
    
        hullDamageText = self.getElementText('damage')
        if (damageType != 'ion' and len(hullDamageText) > 0
             and int(hullDamageText) != -1):
            if isCrewDamage:
                hullDamageText = str(int(hullDamageText) * 15)
            totalXDamage += int(hullDamageText)

        if len(xDamageText) > 0:
            totalXDamage += int(xDamageText)

        totalXDamageText = str(totalXDamage)
        if (len(totalXDamageText) > 0 and
            totalXDamageText not in self.invalidSysDamageValues):
            damage = float(totalXDamageText)
            totalXDamageText = self.getBoost(totalXDamageText, damageAbbr, damage, isCrewDamage)

        if len(totalXDamageText) > 0 and totalXDamageText != '0':
            columnText = totalXDamageText

        return columnText

    def getIonDamage(self) -> str:
        if 'I' not in self.validColumns:
            return
        # use the getDamagePlusXDamage but bypass the part where
        # hullDamage is added to the damage total
        columnText = self.getDamagePlusXDamage('ion')
        if 'ION_PIERCE_CHAIN' in self.blueprintName:
            columnText = columnText.replace('title="', 'title="' + phaserAbbrText + " ")
        elif 'ION_PIERCE' in self.blueprintName:
            columnText = phaserAbbr.format(int(columnText))
        self.columnValues.append(columnText)
        return columnText

    # Accepts number that is str
    # if text is "''", pass ValueError exception
    def strToInt(self, number: str) -> int:
        intVal = 0
        try:
            intVal = int(number)
        except:
            pass
        return intVal

    # Number of shots. Appends Accuracy template if there's an
    # accuracyMod elem
    def getShots(self) -> str:
        if 'Shots' not in self.validColumns:
            return
        columnText = self.getElementText('shots')

        # get projectiles (Flak, burst, etc)
        typeElem = self.blueprint.find('type')
        if typeElem.text == 'BURST':

            projectileCount = 0
            projectilePath = './/projectiles/projectile[@fake="false"]'
            for projectileElem in self.blueprint.findall(projectilePath):
                projectileCount += int(projectileElem.get('count'))

            if len(columnText) > 0:
                projectileCount *= int(columnText)
            columnText = str(projectileCount)

        # chargeLevels
        chargeLevelsText = self.getElementText('chargeLevels')
        if len(chargeLevelsText) > 0:
            columnText += f'-{chargeLevelsText}'

        # missile cost
        missilesText = self.getElementText('missiles')
        if len(missilesText) > 0 and int(missilesText) != 0:
            # beams do not consume missiles
            if typeElem.text != 'BEAM':
                columnText += '/'
            columnText += f'{missilesText}{icons["missile"]}'

        # accuracy
        accuracyMod = self.getElementText('accuracyMod')
        if len(accuracyMod) > 0:
            accuracyIcon = icons["accuracy"].replace("num", accuracyMod)
            columnText += f'{accuracyIcon}'

        # drone_targetable = 0
        drone_targetable_text = self.getElementText('drone_targetable')
        if drone_targetable_text == '0' and typeElem.text == 'MISSILES':
            columnText += f'{icons["non_drone_targetable"]}'
            
        self.columnValues.append(columnText)
        return columnText

    def getPierce(self) -> str:
        if 'Pierce' not in self.validColumns:
            return
        columnText = ''

        spText = self.getElementText('sp')
        if len(spText) > 0:
            if int(spText) < 0:
                columnText = ''
            elif int(spText) != 0:
                columnText = spText

        self.columnValues.append(columnText)
        return columnText

    def getRadius(self) -> str:
        if 'Radius' not in self.validColumns:
            return
        columnText = self.getElementText('radius')
        if len(columnText) > 0:
            if int(columnText) == 0:
                columnText = ''
            else:
                columnText += 'px'
        self.columnValues.append(columnText)
        return columnText

    def getLength(self) -> str:
        if 'Length' not in self.validColumns:
            return
        
        columnText = self.getElementText('length')
        if len(columnText) > 0:
            if int(columnText) == 0:
                columnText = ''
            else:
                columnText += 'px'
        self.columnValues.append(columnText)
        return columnText

    def getPower(self) -> str:
        if 'Power' not in self.validColumns:
            return

        columnText = self.getElementText('power')
        # abbr for power-providing weapons
        if len(columnText) > 0 and int(columnText) < 0:
            power = -1 * int(columnText)
            columnText = (
                f'<abbr title="Provides {power} power to the weapon to its '
                f'right.">{columnText}</abbr>'
            )
        self.columnValues.append(columnText)
        return columnText

    def getCooldown(self) -> str:
        if 'Cooldown' not in self.validColumns:
            return

        columnText = self.getElementText('cooldown')
        # cooldown boost

        if (len(columnText) > 0 and
            math.isclose(float(columnText), 0, rel_tol=1e-18)):
             # weapons that start charged
            columnText = startChargedAbbr
        elif len(columnText) > 0 and float(columnText) < 0:
            columnText = ''
        else:
            boostElem = self.blueprint.find('boost')

            if (boostElem is not None and
                boostElem.find('.//type').text == 'cooldown'):
                # assume cooldown nonzero if boost present
                cooldownMax =  float(columnText)
                columnText = self.getBoost(columnText, cooldownAbbr, cooldownMax)

                # INSTANT / pre-emptive weapon (no cooldown)
                if len(columnText) == 0:
                    columnText = preemptAbbr.format(cooldownMax)

        fireTimeElem = self.blueprint.find('fireTime')
        if fireTimeElem is not None:
            columnText += self.getFireTime(fireTimeElem)

        self.columnValues.append(columnText)
        return columnText

    # for boost types: damage, cooldown
    def getBoost(self, columnText: str, abbr: str, startVal: float, isCrewDamage: bool = False) -> str:
        boostElem = self.blueprint.find('boost')
        if boostElem is None:
            return columnText

        amount = float(boostElem.find('.//amount').text)
        if isCrewDamage:
            amount *= 15
        count = int(boostElem.find('.//count').text)
        endVal = 0
        change = (amount * count)

        # infinitely increasing
        if count == 999:
            abbr = infiniteAbbr
            columnText = abbr.format(startVal, amount)
            return columnText


        if boostElem.find('.//type').text == 'cooldown':
            if abbr != cooldownAbbr:
                if int(startVal) == startVal and isinstance(startVal, float):
                    startVal = int(startVal)
                return str(startVal)
            endVal = startVal - change
        else:
            endVal = startVal + change

        if endVal >= 0:
            columnText = abbr.format(startVal, endVal, amount, count)           
        else:
            # INSTANT / pre-emptive weapon (no cooldown)
            columnText = ''
        return columnText

    def getFireTime(self, fireTimeElem: ET.Element) -> str:
        columnText = ''
        fireTime = float(fireTimeElem.text)
        fireTimeNotDefault = math.isclose(fireTime, 0.25, rel_tol=1e09)
        if fireTimeNotDefault:
            columnText = f'/{fireTimeAbbr.format(fireTime)}'
        return columnText

    def getFireChance(self) -> str:
        if 'Fire' not in self.validColumns:
            return

        columnText = self.getPercent(self.getElementText('fireChance'))
        self.columnValues.append(columnText)
        return columnText

    def getBreachChance(self) -> str:
        if 'Breach' not in self.validColumns:
            return

        columnText = self.getPercent(self.getElementText('breachChance'))
        self.columnValues.append(columnText)
        return columnText

    # compatible if stunChance and stun ever can occur simultaneously
    def getStun(self) -> str:
        if 'Stun' not in self.validColumns:
            return
        stunChanceElem = self.blueprint.find('stunChance')
        stunElem = self.blueprint.find('stun')

        columnText = ''
        if stunChanceElem is None and stunElem is None:
            self.columnValues.append(columnText)
            return ''

        if stunChanceElem is not None and stunChanceElem.text == '0':
            self.columnValues.append(columnText)
            return ''

        if stunChanceElem is None:
            columnText += '100%'
        else:
            columnText += self.getPercent(stunChanceElem.text)

        if stunElem is None:
            columnText += ' (3s)'
        else:
            columnText += f' ({stunElem.text}s)'

        self.columnValues.append(columnText)
        return columnText

    def getFreeMissileChance(self) -> str:
        if 'Free Missile Chance' not in self.validColumns:
            return
        columnText = ''

        freeMissileChanceText = self.getElementText('freeMissileChance')
        if len(freeMissileChanceText) > 0:
            columnText += freeMissileChanceText + '%'

        self.columnValues.append(columnText)
        return columnText

    def getPercent(self, chanceBaseOne: str) -> str:
        if len(chanceBaseOne) == 0 or int(chanceBaseOne) == 0:
            return ''
        percentChance = int(chanceBaseOne) * 10
        return f'{percentChance}%'

    def getCost(self) -> str:
        if 'Cost' not in self.validColumns:
            return
        columnText = self.getElementText('cost')
        if len(columnText) == 0:
            columnText = '0'

        columnText += f' {icons["scrap"]}'
        self.columnValues.append(columnText)
        return columnText

    def getRarity(self) -> str:
        if '[[Rarity]]' not in self.validColumns:
            return
            
        columnText = self.getElementText('rarity')
        self.columnValues.append(columnText)
        return columnText

    def getSpeed(self) -> str:
        if 'Speed' not in self.validColumns:
            return

        columnText = self.getElementText('speed')
        if len(columnText) == 0:
            typeText = self.blueprint.find('type').text

            if typeText in defaultSpeeds:
                columnText = defaultSpeeds[typeText]
        elif len(columnText) > 0 and int(columnText) == 0:
            columnText = ''
        self.columnValues.append(columnText)
        return columnText

    def getEffects(self) -> str:
        if 'Effects' not in self.validColumns:
            return
        columnText = ''
        columnText += self.getSilencedEffect()
        # effectsList = []
        # effectsList.append(self.getSilencedEffect())
        # columnText += ', '.join(effectsList)
        
        self.columnValues.append(columnText)
        return columnText

    def getSilencedEffect(self) -> str:
        statBoostsElem = self.blueprint.find('statBoosts')
        if statBoostsElem is not None:
            for statBoostElem in statBoostsElem.findall('statBoost'):
                if statBoostElem.get('name') == 'silenced':
                    return 'Silenced'
        return ''

    def getElementText(self, tag: str) -> str:
        elem = self.blueprint.find(tag)
        if elem is None:
            return ''
        return elem.text
