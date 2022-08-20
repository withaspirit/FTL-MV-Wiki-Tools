import blueprintUtils as blueprintUtils
import xml.etree.ElementTree as ET
import time

# Compare 2 files
# New version must be in 'FTL Data/data/'
# Old version must be specified in 'oldVersionPath' variable


# Get names of blueprints added, removed and changed between updates
# Also get blueprints whose title/class were changed after update

# TODO: look at hyperspace.xml for crew
oldVersionPath = blueprintUtils.cwd + '/old data/data/'

paths = [
    './crewBlueprint[@name]',
    './weaponBlueprint[@name]',
    './augBlueprint[@name]',
    './droneBlueprint[@name]',
    './shipBlueprint[@name]'
]

# Get 'name' attributes of blueprints in a file
def getBlueprintNames(root: ET.Element) -> list[str]:
    blueprintNameList = []
    for path in paths:
        bps = root.findall(path)
        for bp in bps:
            name = bp.get('name')
            blueprintNameList.append(name)

    return blueprintNameList

# Get map of blueprints [name, title/class]
def getBlueprintNameAndTitle(root: ET.Element) -> dict[str, str]:
    blueprintNameTitleDict = {}
    for path in paths:
        bps = root.findall(path)
        for bp in bps:
            name = bp.get('name')
            title = ''
            if path == './shipBlueprint[@name]':
                title = bp.find('class').text
            else:
                title = bp.find('title').text
            blueprintNameTitleDict.update({name : title})

    return blueprintNameTitleDict

# Get the difference between two lists while maintaining insertion order
def orderedDifference(list1: list, list2: list) -> list:
    set2 = set(list2)
    differentElements = []
    for elem in list1:
        if elem not in set2:
            differentElements.append(elem)
    return differentElements

# Currently limited to comparing blueprints.xml and dlcBlueprints.xml
if __name__ == '__main__':
    start_time = time.time()
    newBlueprints = blueprintUtils.getBlueprints()
    newDLCBlueprints = blueprintUtils.getDLCBlueprints()

    oldBlueprints = blueprintUtils.getBlueprints(oldVersionPath)
    oldDLCBlueprints = blueprintUtils.getDLCBlueprints(oldVersionPath)

    oldBlueprintNames = []
    oldBlueprintNames += getBlueprintNames(oldBlueprints)
    oldBlueprintNames += getBlueprintNames(oldDLCBlueprints)

    newBlueprintNames = []
    newBlueprintNames += getBlueprintNames(newBlueprints)
    newBlueprintNames += getBlueprintNames(newDLCBlueprints)

    oldBlueprintsRemoved = orderedDifference(oldBlueprintNames, newBlueprintNames)
    newBlueprintsAdded = orderedDifference(newBlueprintNames, oldBlueprintNames)
    # oldBlueprintsRemoved = sorted(set(oldBlueprintNames) - set(newBlueprintNames), key=oldBlueprintNames.index)
    # newBlueprintsAdded = sorted(set(newBlueprintNames) - set(oldBlueprintNames), key=newBlueprintNames.index)

    compareText = '\nOld blueprints removed\n\n'
    compareText += '\n'.join(oldBlueprintsRemoved)
    compareText += '\n\nNew blueprints added\n\n'
    compareText += '\n'.join(newBlueprintsAdded)

    newBlueprintNameTitle = getBlueprintNameAndTitle(newBlueprints)
    oldBlueprintNameTitle = getBlueprintNameAndTitle(oldBlueprints)

    commonBlueprintNames = sorted(newBlueprintNameTitle.keys() & oldBlueprintNameTitle.keys())
    differentTitles = {}
    for name in commonBlueprintNames:
        newTitle = newBlueprintNameTitle[name]
        oldTitle = oldBlueprintNameTitle[name]
        if newTitle != oldTitle:
            differentTitles.update({name : [oldTitle, newTitle]})

    compareText += '\n\nDifferent titles:\n\n'

    for key, value in differentTitles.items():
        compareText += f'\n {key}: {value}'

    compareVersionsFile = open(blueprintUtils.cwd + '\compareVersions.txt', 'w', encoding='utf-8')
    compareVersionsFile.write(compareText)
    compareVersionsFile.close()
    print('--- %s seconds ---' % (time.time() - start_time))

