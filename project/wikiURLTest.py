import blueprintUtils as blueprintUtils
import urllib.request
import re
import time

# verifies that the wikiHeading of each blueprint is found on its corresponding page
# takes ~ 5-7 minutes

filePath = blueprintUtils.wikiElementsPath
files = {
    'blueprints.xml.append',
    'autoBlueprints.xml.append',
    'dlcBlueprints.xml.append'
}

urlRegex = re.compile('>(https:\/\/.+)<')
def getUrls() -> set[str]:
    urlsToTest = set()
    for fileName in files:
        with open(filePath + fileName, encoding='utf-8') as file:
            fileText = file.read()
            urlsToTest.update(urlRegex.findall(fileText))
    return urlsToTest

def getHeading(url: str) -> str:
    heading = url.replace('https://ftlmultiverse.fandom.com/wiki/', '')
    pageEnd = heading.find('#') 
    if pageEnd != -1:
        heading = heading[pageEnd + 1:]
    
    return heading.replace("_", " ")

if __name__ == '__main__':
    start_time = time.time()
    urlsToTest = getUrls()

    nonFunctioningUrls = []
    badHeadingUrls = []
    notFoundUrls = []

    for url in urlsToTest:
        # make url parsable
        newUrl = url.replace("'", '%27')
        #print(newUrl)
        try:
            with urllib.request.urlopen(newUrl) as f:
                text = f.read().decode('utf-8')

                if 'There is currently no text in this page.' in text:
                    nonFunctioningUrls.append(newUrl)
                else:
                    # determine whether 'heading' is in text
                    heading = getHeading(url)
                    if heading not in text:
                        badHeadingUrls.append(newUrl)
                
        except urllib.error.HTTPError as e:
            notFoundUrls.append(newUrl)
            pass

    badUrls = "\n".join(badHeadingUrls)
    notFoundUrls = "\n".join(notFoundUrls)
    print(f'Non-functioning urls: {nonFunctioningUrls}')
    print(f'Bad urls: {badUrls}')
    print(f'Not found urls: {notFoundUrls}')

    print('--- %s seconds ---' % (time.time() - start_time))
