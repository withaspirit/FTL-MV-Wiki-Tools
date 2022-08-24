import blueprintUtils as blueprintUtils
import xml.etree.ElementTree as ET

#     files used
#     blueprints.xml (always)
#     dlcBlueprints.xml (some)
#     autoblueprints.xml (some)
#     hyperspace.xml (always)
#     text_blueprints.xml (always)
#     events_boss.xml (always)
pathToData = blueprintUtils.pathToData
class Ship:

    # defaultStartPower, defaultMaxPower
    systems = {
        'shields': (2, 8),
        'engines': (1, 8),
        'oxygen': (1, 3),
        'weapons': (1, 8),
        'drones': (2, 8),
        'clonebay': (1, 3),
        'medbay': (1, 3),
        'teleporter': (1, 3),
        'cloaking': (1, 5),
        'artillery': (1, 4),
        'mind': (1, 3),
        'hacking': (1, 3),
        'temporal': (1, 3),
        'pilot': (1, 3),
        'sensors': (1, 3),
        'doors': (1, 3),
        'battery': (1, 2)
    }

    # opening files once and passing instead of opening them many times
    # significantly reduces runtime
    def __init__(self, blueprint, blueprints, hyperspace, text_blueprints, events_boss):
        self.blueprint = blueprint
        self.blueprints = blueprints
        self.blueprintName = self.blueprint.get('name')

        self.hyperspace = hyperspace
        self.text_blueprints = text_blueprints
        self.events_boss = events_boss
        customShipPath = f'.//ships/customShip[@name="{self.blueprintName}"]'
        self.customShip = hyperspace.find(customShipPath)

    # print in format for wiki
    def toString(self) -> str:
        text = self.getHeading()
        text += self.getDescription()
        text += self.getImages()
        text += self.getDefaultName()
        text += self.getStartingCrew()
        text += self.getStartingReactor()
        text += self.getMaxHull()
        text += self.getCrewCapacity()
        text += self.getSystemLimit()
        text += self.getStartingSystems()
        text += self.getInvalidSystems()
        text += self.getStartingWeapons()
        text += self.getStartingDrones()
        text += self.getStartingAugments()
        text += self.getHiddenAugments()
        text += self.getStartingResources()
        text += self.getSlots()
        text += self.getLastStandEntryText()
        text += self.getUnlock()
        return text

    def getHeading(self) -> str:
        headingElement = self.getElement('wikiHeading')
        if headingElement is None:
            print(f'wikiHeading needs to be generated for {self.blueprintName}')
            headingElement = self.getElement('name')

        heading = headingElement.text
        return f"\n=='''{heading}'''=="

    def getDescription(self) -> str:
        desc = self.getElement('desc').text
        return f"\n''{desc}''"

    def getImages(self) -> str:
        shipName = self.getElement('name').text
        shipImg = self.getAttribute('img') + " base"
        shipImg = shipImg.capitalize()
        shipImg = shipImg.replace("_", " ")

        if self.blueprintName == 'PLAYER_SHIP_VANILLA':
            shipName += ' (Alpha)'
        elif 'VANILLA' in self.blueprintName:
            shipName = 'VANILLA ' + shipName

        return f" [[File:{shipName}.jpg|thumb|400px]][[File:{shipImg}.png|thumb|400px]]"

    def getDefaultName(self) -> str:
        shipName = self.getElement('name').text
        return f"\n* Default Name: {shipName}"

    def getStartingCrew(self) -> str:
        crewMap = self.getCrewMap()

        startingCrew = f"\n* Starting Crew: "
        if len(crewMap.keys()) == 0:
            startingCrew += "None"
            return startingCrew

        crewList = []
        for linkCountPair in crewMap.values():
            crewLink = linkCountPair[0]
            crewCount = linkCountPair[1]
            crewString = f'{crewCount} {crewLink}'
            crewList.append(crewString)

        startingCrew += ', '.join(crewList)
        return startingCrew

    def getCrewMap(self) -> dict[str, list]:
        crewMap = {}

        # parse hyperspace.xml
        crewElements = self.customShip.find('crew')
        if crewElements:
            for i, crewElement in enumerate(crewElements):
                blueprintName = crewElement.tag
                customName = crewElement.get('name')

                # blueprintName already visited
                if blueprintName in crewMap:
                    crewMap[blueprintName][1] += 1
                    continue

                blueprintLink = self.getBlueprintLink(blueprintName, 'crewBlueprint', customName)

                # make crew with customName count as 1 crew; distinguish from other crew and duplicates
                if blueprintLink[-1] == "'": # is customName
                    blueprintName += str(i)

                if blueprintName not in crewMap:
                    crewMap.update({blueprintName : [blueprintLink, 0]})
                crewMap[blueprintName][1] += 1

        # parse blueprints.xml
        crewCountElements = self.blueprint.findall('crewCount')
        if crewCountElements:
            for crewCountElement in crewCountElements:
                amount = int(crewCountElement.get('amount'))
                blueprintName = str(crewCountElement.get('class'))

                if blueprintName in crewMap:
                    crewMap[blueprintName][1] += amount
                    continue

                blueprintLink = self.getBlueprintLink(blueprintName, 'crewBlueprint')
                crewMap.update({blueprintName : [blueprintLink, amount]})
        return crewMap

    def getStartingReactor(self) -> str:
        maxPower = self.getElementAttribute('maxPower', 'amount')
        startingReactor = f'\n* Starting Reactor: {maxPower}'

        customReactorPath = './/customReactor'
        customReactorElement = self.customShip.find(customReactorPath)
        if customReactorElement is None:
            return startingReactor

        customMax = int(customReactorElement.get('maxLevel'))
        if customMax != 30:
            startingReactor += f" '''[Max {customMax}]'''"

        return startingReactor

    def getMaxHull(self) -> str:
        maxHull = self.getElementAttribute('health', 'amount')
        if maxHull != '30':
            maxHull =  f"'''{maxHull}'''"
        return f'\n* Max Hull: {maxHull}'

    def getCrewCapacity(self) -> str:
        crewLimitElement = self.customShip.find('crewLimit')
        crewLimit = ''
        if crewLimitElement is None:
            # crewLimitElement not present when crewLimit is the default, 8
            crewLimit = '8'
        else:
            crewLimit = f"'''{crewLimitElement.text}'''"

        return f'\n* Crew Capacity: {crewLimit}'

    def getSystemLimit(self) -> str:
        systemLimitElement = self.customShip.find('systemLimit')
        if systemLimitElement is None:
            return ''

        systemLimit = systemLimitElement.text
        return f"\n* System Limit: '''{systemLimit}'''"

    def getStartingSystems(self) -> str:
        systemsList = self.getSystemsList()
        # len(systemList) never 0
        startingSystems = '\n* Starting Systems\n** ' + '\n** '.join(systemsList)
        return startingSystems

    # FIXME: this function is awfully long
    def getSystemsList(self) -> list[str]:
        systemList = self.blueprint.find('systemList')

        systemsList = []
        for (systemName, systemSettings) in self.systems.items():
            systemElements = systemList.findall(systemName)
            if len(systemElements) == 0: # system not on ship
                continue

            # only with 'artillery' can there be more than one copy of a system
            for systemElement in systemElements:

                systemAppend = self.getSystemAppend(systemElement, systemSettings)
                if systemAppend == 'continue':
                    continue

                displayName = systemName
                systemStart = systemElement.get('start')
                systemPower = int(systemElement.get('power'))

                # medbay overrides clonebay if 'start="true"' for both
                # this could be written better
                if (displayName == 'medbay' and systemStart == 'true' and
                    'Clone' in systemsList[len(systemsList) - 1]):
                    del systemsList[len(systemsList) - 1]

                # this could be a method?
                if displayName == 'artillery':
                    artilleryName = systemElement.get('weapon')
                    if artilleryName in blueprintUtils.nonexistantBlueprints:
                        continue
                    # using getBlueprintList for one element
                    artilleryNames = []
                    artilleryNames.append(artilleryName)
                    displayName = self.getBlueprintList('weaponBlueprint', artilleryNames)[0]
                else:
                    displayName = self.getSystemName(displayName)

                systemString = f'{displayName} '
                if systemStart == 'false':
                    systemString += "'''(0)'''"
                else:
                    systemString += f'({systemPower})'

                systemString += systemAppend
                systemsList.append(systemString)
        return systemsList

    # The following information can be appended after for each system:
    # Whether the 'max' attribute of a system differs from the default value
    # Whether a system's 'power' attribute starts at a non-default value on purchase
    # Whether the system's room is resistant
    def getSystemAppend(self, systemElement: ET.Element, systemSettings: list[str]):
        defaultStartPower = systemSettings[0]
        defaultMaxPower = systemSettings[1]
        systemStart = systemElement.get('start')
        systemMax = systemElement.get('max')
        systemPower = int(systemElement.get('power'))

        differentMax = False
        systemAppend = ''

        # systemMax different than defaultMaxPower or systemPower greater than defaultMaxPower
        systemAppend = ''
        if (systemMax is not None) and (int(systemMax) != defaultMaxPower):
            systemAppend += f" '''[Max {systemMax}]'''"
            differentMax = True
        elif (systemPower > defaultMaxPower):
            systemAppend += f" '''[Max {systemPower}]'''"
            differentMax = True

        # Start Power starts at different value than defaultStartPower on purchase
        if (systemStart == 'false') and (systemPower != defaultStartPower):
            systemAppend += f" [starts at '''{systemPower}''' on purchase]"
        elif (systemStart == 'false') and (differentMax is False):
            return 'continue'

        # Resistant room: System, Ion, or both
        # assume ships start with all resistant rooms they'll have
        roomId = systemElement.get('room')
        sysDamageResistChancePath = f'.//rooms/room[@id="{roomId}"]/sysDamageResistChance'
        sysResist = self.customShip.find(sysDamageResistChancePath)
        ionDamageResistChancePath = f'.//rooms/room[@id="{roomId}"]/ionDamageResistChance'
        ionResist = self.customShip.find(ionDamageResistChancePath)

        ionResistBool = ionResist is not None
        sysResistBool = sysResist is not None

        if not ionResistBool and not sysResistBool:
            return systemAppend

        resistText = 'Resists '
        resistList = []
        if sysResistBool:
            resistList.append('System')
        if ionResistBool:
            resistList.append('Ion')
        resistText += ', '.join(resistList) + ' Damage'
        systemAppend += f" ('''{resistText}''')"
        return systemAppend

    def getSystemName(self, name: str) -> str:
        correctName = name.capitalize()
        if correctName == 'Mind':
            correctName = 'Mind Control'
        elif correctName == 'Pilot':
            correctName = 'Piloting'
        return correctName

    def getStartingWeapons(self) -> str:
        blueprintNames = self.getBlueprintNames('weaponList')
        weaponList = self.getBlueprintList('weaponBlueprint', blueprintNames)

        if len(weaponList) == 0:
            return ''
        return '\n* Starting Weapons\n** ' + '\n** '.join(weaponList)

    def getInvalidSystems(self) -> str:
        invalidSystems = self.getInvalidSystemsList()
        if len(invalidSystems) == 0:
            return ''
        invalidSystemsText = '\n* The following systems cannot be installed:\n** '
        invalidSystemsText += '\n** '.join(invalidSystems)
        return invalidSystemsText

    def getInvalidSystemsList(self) -> list[str]:
        systemList = self.blueprint.find('systemList')

        invalidSystems = []
        for systemName in self.systems:
            # SKIP TEMPORAL
            if systemName == 'temporal':
                continue
            systemElements = systemList.findall(systemName)
            # SKIP ARTILLERY
            if len(systemElements) == 0 and systemName != 'artillery':
                displayName = self.getSystemName(systemName)
                invalidSystems.append(displayName)
        return invalidSystems

    def getStartingDrones(self) -> str:
        blueprintNames = self.getBlueprintNames('droneList')
        droneList = self.getBlueprintList('droneBlueprint', blueprintNames)

        if len(droneList) == 0:
            return ''
        startingDrones = '\n* Starting Drones\n** ' + '\n** '.join(droneList)
        return startingDrones

    def getStartingAugments(self) -> str:
        augElements = self.blueprint.findall('.//aug[@name]')
        blueprintNames = []
        for augElement in augElements:
            augName = augElement.get('name')
            blueprintNames.append(augName)

        augmentList = self.getBlueprintList('augBlueprint', blueprintNames)
        if len(augmentList) == 0:
            return ''

        startingAugments = '\n* Starting Augments\n** ' + '\n** '.join(augmentList)
        return startingAugments

    # as of 5.2.3 only Flagships and Monk Cruisers have these
    def getHiddenAugments(self) -> str:
        hiddenAugments = self.getHiddenAugmentList()
        if len(hiddenAugments) == 0:
            return ''

        return '\n* Hidden Augments\n** ' + '\n** '.join(hiddenAugments)

    def getHiddenAugmentList(self) -> list[str]:
        hiddenAugs = self.customShip.findall('.//hiddenAug')
        hiddenAugments = []

        for hiddenAug in reversed(hiddenAugs):
            augmentName = hiddenAug.text
            firstFourLetters = augmentName[:4]
            if firstFourLetters == 'SHIP' or firstFourLetters == 'FOR_': # ship flavor or 'FOR_MULTIVERSE'
                continue
            hiddenAugmentFormatted = self.getBlueprintLink(augmentName, 'augBlueprint')
            hiddenAugments.append(hiddenAugmentFormatted)

        return hiddenAugments

    def getStartingResources(self) -> str:
        missiles = self.getElementAttribute('weaponList', 'missiles')
        drones = self.getElementAttribute('droneList', 'drones')

        if missiles == '' and drones == '':
            return ''

        startingResources = '\n* Starting Resources'

        if missiles != '' and int(missiles) > 0:
            startingResources += f"\n** {missiles}" + " {{Missile}}"

        if drones != '' and int(drones) > 0:
            startingResources += f"\n** {drones}" + " {{DroneParts}}"

        # make text actually appended
        if startingResources != '\n* Starting Resources':
            return startingResources
        return ''

    def getSlots(self) -> str:
        weaponSlots = int(self.getElement('weaponSlots').text)
        weaponText = f'{weaponSlots} Weapon'
        weaponText = self.pluralize(weaponSlots, weaponText)
        if weaponSlots == 0:
            weaponText = 'No Weapon Slots'

        droneSlots = int(self.getElement('droneSlots').text)
        droneText = f'{droneSlots} Drone'
        droneText = self.pluralize(droneSlots, droneText)
        if droneSlots == 0:
            droneText = 'No Drone Slots'

        teleporterTiles = int(self.blueprint.find('teleporterLimit').text)
        teleporterText = f'{teleporterTiles}-tile Teleporter'
        if teleporterTiles == 0:
            teleporterText = 'No Teleporter Tiles'

        return f'\n* Slots: {weaponText}, {droneText}, {teleporterText}'

    def getLastStandEntryText(self) -> str:
        shipTypeElement = self.customShip.find('hiddenAug')
        shipType = shipTypeElement.text

        if 'SHIP' not in shipType:
            raise Exception(f'shipType not first hiddenAug: {self.blueprintName}')
        lastStandText = self.getLastStandText(shipType)

        lastStandEntryText = f"\n* Last Stand entry text: ''{lastStandText}'' '''({shipType})'''"
        return lastStandEntryText

    def getLastStandText(self, shipType: str) -> str:
        choicePath = './/event[@name="TRUE_LAST_STAND_START"]/choice[@lvl="-2147483648"]'
        choiceElement = self.events_boss.find(choicePath)

        lastStandTextPath = f'.//event/choice[@req="{shipType}"]/event/text'
        lastStandElement = choiceElement.find(lastStandTextPath)
        return lastStandElement.text

    def getUnlock(self) -> str:
        unlockElement = self.getElement('unlock')
        if unlockElement is None:
            return ''

        unlockId = unlockElement.get('id')
        unlockPath = f'.//text[@name="{unlockId}"]'
        unlockBlueprint = self.text_blueprints.find(unlockPath)
        unlockText = unlockBlueprint.text

        unlock = "\n==='''Unlock'''==="
        unlock += f'\n* {unlockText}'
        return unlock

    # Helper methods

    def getElement(self, elementName: str):
        return self.blueprint.find(elementName)

    def getAttribute(self, attribute: str) -> str:
        return self.blueprint.get(attribute)

    def getElementAttribute(self, tag: str, attribute: str) -> str:
        element = self.blueprint.find(tag)
        if element is None:
            return ''
        attribute = element.get(attribute)
        return attribute

        # for weaponList, droneList
    def getBlueprintNames(self, listType: str) -> list[str]:
        blueprintList = self.blueprint.find(listType)
        blueprintNames = []
        if blueprintList is None:
            return blueprintNames

        for blueprint in blueprintList:
            blueprintName = blueprint.get('name')
            blueprintNames.append(blueprintName)
        return blueprintNames

    def getBlueprintList(self, tag: str, blueprintNames: list[str]) -> list[str]:
        blueprintList = []
        for blueprintName in blueprintNames:
            blueprintLink =  self.getBlueprintLink(blueprintName, tag)
            blueprintList.append(blueprintLink)
        return blueprintList

    # FIXME: Try doing this at "appendWikiElements" stage instead of at "wikiShipExport" stage
    # customName is names given to Regular Crew or Secret Crew members (N/A for Unique Crew)
    def getBlueprintLink(self, name: str, tag: str, crewName: ET.Element = None) -> str:
        blueprint = blueprintUtils.findBlueprint(self.blueprints, tag, name)
        wikiRedirect = blueprintUtils.getWikiRedirectWithPlaceholder(blueprint, self.getElement('wikiPage').text)
        wikiName = blueprintUtils.getWikiName(blueprint)
        blueprintLink = ''
        # could condense this into one method
        if crewName is None:
            blueprintLink = blueprintUtils.formatBlueprintLink(wikiRedirect, wikiName)
        else:
            blueprintLink = blueprintUtils.formatCrewBlueprintLink(wikiRedirect, wikiName, crewName)

        # this is done after blueprintLink() function because it shouldn't be part of the link
        if tag == 'augBlueprint':
                blueprintLink = self.augmentProcessing(name, tag, blueprintLink)
        return blueprintLink

    # TODO: check hyperspace.xml if f'augments/aug[@name="{blueprintName}"]' has "locked" element -> (INDICATES LOCKED)
    # TODO: maybe pass hyperspace.xml to ships
    def augmentProcessing(self, blueprintName: str, tag: str, blueprintLink: str) -> str:
        newBlueprintLink = blueprintLink
        blueprint = blueprintUtils.findBlueprint(self.blueprints, tag, blueprintName)
        # augBlueprint should always have title
        title = blueprint.find('title').text

        aug = self.hyperspace.find(f'.//augments/aug[@name="{blueprintName}"]')
        locked = None
        if aug is not None:
            locked = aug.find('locked')

        if locked is not None:
            newBlueprintLink = '{{Lock}} ' + newBlueprintLink
        elif '[M]' in title:
            newBlueprintLink += ' [M]'
        elif '[X]' in title:
            newBlueprintLink += ' [X]'
        elif '[L]' in title:
            newBlueprintLink = '[L] ' + newBlueprintLink
        return newBlueprintLink

    def pluralize(self, number: int,  word: str) -> str:
        if number <= 1:
            return word
        return f'{word}s'
