import xml.etree.ElementTree as ET
import math

# https://ftlmultiverse.fandom.com/wiki/Weapon_Tables

# unused templates: https://ftlmultiverse.fandom.com/wiki/User:Puporongo/Sandbox

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

icons = {
    'rad': '{{RadDebuffIcon}}',
    'scrap': '{{Scrap}}',
    'missile': '{{Missile}}',
    'accuracy': '{{Accuracy|num}}'
}

# Cooldown
cooldownAbbr = (
    '<abbr title="Decreases by {2:g}s after each '
    'volley, down to {1:g}s after {3} volleys.">{0:g}-{1:g}</abbr>'
)
preemptAbbr = '<abbr title="Can only be fired once per fight.">{0:g}</abbr>'
fireTimeAbbr = '<abbr title="Fires projectiles {0:g}s apart.">{0:g}</abbr>'
startChargedAbbr = '<abbr title="Starts charged">0</abbr>'

# TODO: lockdown, special effects (projector),
# TODO: hullbust,
# TODO: damage chain (effects on other damage systems too)
# TODO: free missile chance
# TODO: negative power -> to right of table
# TODO: special case: god killer cooldown
# TODO: Shots -> undetectable by drones
# TODO: medical bomb effects (crew damage)
# TODO: faction column? (transport loot table)
# TODO: chaotic weapon table


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
        self.getHullDamage()
        self.getSysDamage()
        self.getCrewDamage()
        self.getIonDamage()
        self.getPierce()
        self.getShots()
        self.getRadius()
        self.getLength()
        self.getPower()
        self.getCooldown()
        self.getFireChance()
        self.getBreachChance()
        self.getStun()
        self.getCost()
        self.getRarity()
        self.getSpeed()

        return '||'.join(self.columnValues)

# SPECIAL COLUMNS
# EVENT_WEAPONS: faction column
#
# CLONE_CANNON: Table
#
# special effects:
# ZOLTAN_DELETER
# SALT_LAUNCHER
# GASTER_BLASTER -> noSysDamage = false
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

    # TODO: damage boost
    def getHullDamage(self):
        if 'H' not in self.validColumns:
            return

        columnText = self.getElementText('damage')
        if columnText == '-1' or columnText == '0':
            columnText = ''
        self.columnValues.append(columnText)


    invalidSysDamageValues = {'0', '-1'}

    def getSysDamage(self) -> str:
        if 'S' not in self.validColumns:
            return

        columnText = ''
        xDamageText = self.getElementText('sysDamage')

        # damage is added with sysDamage
        if (self.getElementText('noSysDamage') != 'true' and
            xDamageText not in self.invalidSysDamageValues):
            columnText = self.getDamagePlusXDamage(xDamageText)

        self.columnValues.append(columnText)

    radStatBoosts = ['moveSpeedMultiplier', 'stunMultiplier', 'repairSpeed']
    def getCrewDamage(self) -> str:
        if ('C' not in self.validColumns):
            return

        columnText = ''
        xDamageText = self.getElementText('persDamage')

        # damage is added with persDamage
        if (self.getElementText('noPersDamage') != 'true' and
            xDamageText not in self.invalidSysDamageValues):
            columnText = self.getDamagePlusXDamage(xDamageText)
            if len(columnText) > 0:
                columnText = str(int(columnText) * 15)

        # get RAD Debuff if necessary
        columnText += self.getRadDebuff()

        self.columnValues.append(columnText)

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

    # Adds hull damage to xDamage text
    def getDamagePlusXDamage(self, xDamageText: str) -> str:
        columnText = ''
        xDamage = 0
        hullDamageText = self.getElementText('damage')

        xDamage += self.strToInt(hullDamageText)
        xDamage += self.strToInt(xDamageText)
        if xDamage != 0:
            columnText = str(xDamage)
        return columnText

    def getIonDamage(self) -> str:
        if 'I' not in self.validColumns:
            return

        columnText = self.getElementText('ion')
        if columnText == '0':
            columnText = ''
        self.columnValues.append(columnText)

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

        # TODO: drone targetable, ammo cost
        # chargeLevels
        chargeLevelsText = self.getElementText('chargeLevels')
        if len(chargeLevelsText) > 0:
            columnText += f'-{chargeLevelsText}'

        # missile cost
        missilesText = self.getElementText('missiles')
        if len(missilesText) > 0 and int(missilesText) != 0:
            columnText += f'/{missilesText}{icons["missile"]}'

        # accuracy
        accuracyMod = self.getElementText('accuracyMod')
        if len(accuracyMod) > 0:
            accuracyIcon = icons["accuracy"].replace("num", accuracyMod)
            columnText += f' {accuracyIcon}'
        self.columnValues.append(columnText)
        return columnText

    # TODO: damage boost
    def getPierce(self) -> str:
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
        columnText = self.getElementText('radius')
        if len(columnText) > 0:
            if int(columnText) == 0:
                columnText = ''
            else:
                columnText += 'px'
        self.columnValues.append(columnText)
        return columnText

    def getLength(self) -> str:
        columnText = self.getElementText('length')
        if len(columnText) > 0:
            if int(columnText) == 0:
                columnText = ''
            else:
                columnText += 'px'
        self.columnValues.append(columnText)
        return columnText

    def getPower(self) -> str:
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
                columnText = self.getBoostCooldown(boostElem, float(columnText))

        fireTimeElem = self.blueprint.find('fireTime')
        if fireTimeElem is not None:
            columnText += self.getFireTime(fireTimeElem)
            

        self.columnValues.append(columnText)
        return columnText

    def getBoostCooldown(self, boostElem: ET.Element, cooldownMax: float) -> str:
        columnText = ''

        amount = float(boostElem.find('.//amount').text)
        count = int(boostElem.find('.//count').text)
        cooldownMin = cooldownMax - (amount * count)

        if cooldownMin >= 0:
            columnText = cooldownAbbr.format(cooldownMax, cooldownMin, amount, count)           
        else:
            # INSTANT / pre-emptive weapon (no cooldown)
            # TODO: make symbol/template? 
            columnText = preemptAbbr.format(cooldownMax)
        return columnText

    def getFireTime(self, fireTimeElem: ET.Element) -> str:
        columnText = ''
        fireTime = float(fireTimeElem.text)
        fireTimeNotDefault = math.isclose(fireTime, 0.25, rel_tol=1e09)
        if fireTimeNotDefault:
            columnText = f'/{fireTimeAbbr.format(fireTime)}'
        return columnText

    def getFireChance(self) -> str:
        columnText = self.getPercent(self.getElementText('fireChance'))
        self.columnValues.append(columnText)

    def getBreachChance(self) -> str:
        columnText = self.getPercent(self.getElementText('breachChance'))
        self.columnValues.append(columnText)

    def getStun(self) -> str:
        stunChanceElem = self.blueprint.find('stunChance')
        stunElem = self.blueprint.find('stun')

        columnText = ''
        if stunChanceElem is None and stunElem is None:
            self.columnValues.append(columnText)
            return

        if stunChanceElem is None:
            columnText += '100%'
        else:
            columnText += self.getPercent(stunChanceElem.text)

        if stunElem is None:
            columnText += ' (3s)'
        else:
            columnText += f' ({stunElem.text}s)'

        self.columnValues.append(columnText)

    def getPercent(self, chance: str) -> str:
        if len(chance) == 0 or int(chance) == 0:
            return ''

        percentChance = int(chance) * 10
        return f'{percentChance}%'

    def getCost(self) -> str:
        columnText = self.getElementText('cost')
        if len(columnText) == 0:
            columnText = '0'

        columnText += icons["scrap"]
        self.columnValues.append(columnText)

    def getRarity(self) -> str:
        columnText = self.getElementText('rarity')
        self.columnValues.append(columnText)

    # TODO: laser speed (default 60?)
    # TODO: no speed (-)? (seen on bombs in event weapons)
    def getSpeed(self) -> str:
        columnText = self.getElementText('speed')
        self.columnValues.append(columnText)

    def getElementText(self, tag: str) -> str:
        elem = self.blueprint.find(tag)
        if elem is None:
            return ''
        return elem.text