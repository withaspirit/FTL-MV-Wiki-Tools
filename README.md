# FTL: Multiverse Game Data to Wiki Script


# Notes: 

How this mod affects game data is untested. Your game data could become corrupted and unusable. Backing up game data before using patching FTL: Multiverse with anything mitigates that issue. On Windows, the game data is commonly located in the folder `Documents/My Games/FasterThanLight`. Copy all files in the folder to another folder for safekeeping.

# Requirements:

- The game [FTL: Faster Than Light](https://en.wikipedia.org/wiki/FTL:_Faster_Than_Light)
- The mod [FTL: Multiverse](https://subsetgames.com/forum/viewtopic.php?f=11&t=35332) 5.0+ and everything it requires
- [Python 3.9.2 or greater](https://www.python.org/downloads)
- Load order: In [SlipstreamModManager](https://subsetgames.com/forum/viewtopic.php?t=17102), all the mods should be patched after FTL: Multiverse

# Explanation

## Problem

In FTL: Faster Than Light, game data is contained in [XML files](https://en.wikipedia.org/wiki/XML). Each in-game object has a blueprint: an XML element, detailing the object and dictating its behavior.

The original idea was to create a script to extract each [Player Ship's](https://ftlmultiverse.fandom.com/wiki/Player_ships) game data and output it in a format matching the Wiki, allowing ships to be easily updated by copy-pasting the output of the script. 

The problem is that in-game blueprints do not contain enough information to determine what wikiPage they belong to. This means that the output script for the ships would lack hyperlinks to crew, weapons, drones, and other items they feature. Additionally, details like a blueprint's in-game name do not always match its heading or how it is referred to on the Wiki.

To support hyperlinks in the output text, a solution must address the hyperlink problem, which consists of two parts:

1. Match blueprints to their wikiPages
2. Override blueprint information where it doesn't match the Wiki 

## Solution

 The overall solution involves three steps. The first step solves the hyperlink problem. The second step adds elements to existing game files. The third step uses the added elements to generate the output text.

### Step 1: The Hyperlink Problem

The first step involves a .append file, [autoBlueprints.xml.append](./project/Append%20Wiki%20blueprintLists/data/autoBlueprints.xml.append). It is an XML file containining blueprintLists. Each contained blueprintList has a wikiPage as an attribute. For its elements, it has the `"name"` attributes of all blueprints found on that wikiPage. blueprints are uniquely identified by their `name` attribute. The association between blueprints and their wikiPage using blueprintLists solves the first part of the hyperlink problem.

Solving the second part must deal with blueprint information not matching the Wiki. Where a blueprint's information does not match the Wiki, the following information is added as attributes):
- `wikiName`: how an item is referred to on the Wiki
- `wikiHeading`: the heading used to locate an item on a wikiPage

With these attributes, each `<name>` element is provided the necessary information for how its blueprint should be referred to and where it's located on the Wiki. Where these attributes are omitted, it is assumed that the information in the blueprint matches the information on the Wiki.

## Step 2: Adding Information

The second step requires the [autoBlueprints.xml.append](./project/Append%20Wiki%20blueprintLists/data/autoBlueprints.xml.append) file to be added to the game's existing files using SlipstreamModManager. After that, a script called [appendWikiElements.py](./project/appendWikiElements.py) is generate .append files adding the attributes from the `<name>` elements to their corresponding blueprints. The attributes are added as elements. Where the attributes were omitted, information is taken from the game files.

# Step 3:

The last step requires the generated .append files to be added to the game files. That requires each blueprint has information on where it's located on the Wiki. After that, a script called [wikiShipExport.py](./project/wikiShipExport.py) is used to extract information from the game files and format it for the Wiki. The resulting file is inserted in a file called [wikiShips.txt](./project/wikiShips.txt).

# Instructions

### Disclaimer

How this mod affects game data is untested. Your game data could become corrupted and unusable. Therefore, it is recommended to backup game data before using this mod. On Windows, the game data is commonly located in the folder `Documents/My Games/FasterThanLight'. Copy all files in the folder to another folder for safekeeping.

## Step 0: Requirements

This project requires Python version 3.9.2 or later. If Python is not installed on your system, install it [here](https://www.python.org/downloads/). Download any version of python 3.X.Y, where X >= 9 and Y >= 2.

## Step 1. Add blueprintLists

1. If you haven't modified [autoBlueprints.xml.append](./project/Append%20Wiki%20blueprintLists/data/autoBlueprints.xml.append), go to [SlipstreamModManager Process step 2](#slipstreammodmanager-process), with {modName} as `Append Wiki blueprintLists`.
2. If [autoBlueprints.xml.append](./project/Append%20Wiki%20blueprintLists/data/autoBlueprints.xml.append) was modified, go to [SlipstreamModManager Process](#slipstreammodmanager-process), with with {modName} being 'Append Wiki blueprintLists'.

# Step 2. Add Information

- After following Step 1. There are multiple options:
    - [run from terminal](#running-from-terminal-step-2) (easier for beginners)
    - [run from IDE](#running-from-ide) (better option for editing and development) (INCOMPLETE)

### Running from Terminal Step 2

1. Complete the [Running from Terminal](#running-from-terminal) instructions to open the terminal and navigate to the correct directory.
2. Enter in terminal `python ./appendWikiElements.py`. This activates the script and creates the .append files in the [Append wikiElements](./project/Append%20wikiElements/data) folder.
3. Go to [SlipstreamModManager Process](#slipstreammodmanager-process) step 1, with {modName} being `Append wikiElements`.

# Step 3. Export Ships

1. If the terminal was closed, or the directory changed, repeat the [Running from Terminal](#running-from-terminal) instructions.
2. Enter in terminal `python ./wikiShipExport.py`. This activates the script [wikiShipExport.py](./project/wikiShipExport.py), which outputs text to [wikiShips.txt](./project/wikiShips.txt)


## SlipstreamModManager Process:

Make sure that ZIP files are recognized by SlipstreamModManager. To enable this, in SlipstreamModManager, click in this sequence: `File -> Preferences`. In the popup, ensure the `allow_zip` option is checked.

- `{modName}` is a generic name used for the name of the mod's ZIP file.

1. ZIP the 'data' folder in the `{modName}` folder.
2. Move the ZIP file to `SlipstreamModManager/mods/`. After you've done this once for a specific ZIP file, in the future, you can change the ZIP target path to `SlipstreamModManager/mods/` and overwrite the existing ZIP file instead of moving it from the local directory.
3. In SlipstreamModManager folder, double-click `modman.jar` to start SlipstreamModManager.
4. In the list of mods, check the `{modName}` file.
5. Click 'Validate' to ensure the `{modName}` file contains valid XML. Ignore warnings about the invalid character '🗲'. For other warning messages, fix it using the information provided by SlipstreamModManager.
5. 'Patch' FTL with `FTL: Multiverse` and the ZIP file checked. Ensure the ZIP file is listed AFTER FTL: Multiverse. Otherwise, the patch will not work.
6. If you receive a popup asking to start FTL, DO NOT do it. See [Disclaimer](#disclaimer) for details. The popup after patching can be disabled by following the sequence in SlipstreamModManager: `File -> Preferences` and ensuring that 'never_run_ftl' is checked.
7. Do `File-> Extract Dats...` and select the project folder. It is important that the project folder is selected because the scripts rely on the game folders being in the same directory.
8. Click `Save` in the `Extract Dats...` popup. Wait for the files to be extracted.

If coming from [Step 1. Add blueprintLists](#step-1-add-blueprintlists), go to [Step 2. Add Information](#step-2-add-information).

If coming from [Step 2. Add Information](#step-2-add-information), go to [Step 3.](TODO).

- Note that after completing [Step 2](#step-2-add-information), [createShipBlueprintLists.py](./project/createShipBlueprintLists.py) and [appendWikiElements.py](./project/appendWikiElements) will not because the blueprintLists are no longer contained in 'autoBlueprints.xml'. In SlipstreamModManager, doing the following will recreate the environment for the scripts to work correctly:

1. Patch FTL with only FTL: Multiverse selected.
2. `Extract the Dat...` to the [/project/FTL Data](./project/FTL%20Data/) folder.

## Running from Terminal

(Guide for Windows) 

1. In the Windows search bar, type "terminal". The app "Command Prompt" should appear. Click it to open the Command Prompt.
2. Locate and copy the filePath of the project folder, referred to as `projectFilePath`.
3. In the terminal, enter `cd {projectFilePath}/project`. This changes the working directory of the terminal to where the script is.

<img src="images/runFromTerminal.png" alt="Image containing terminal commands">

## Running from IDE
[INCOMPLETE]

# Development Tools
- Windows 10
- [Python 3.9.2](https://www.python.org/downloads)
- [Visual Studio Code](https://code.visualstudio.com/)
- [SlipstreamModManager](https://subsetgames.com/forum/viewtopic.php?t=17102)

