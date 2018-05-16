# Processes links and saves the required data.
# Written by Louis Kennedy

import Networker as network
import RecipeParser as parser
import re
import Settings

mainlinks = []
processedlinks = []
rparser = parser.RecipeParser(Settings.BASE_SERVER)
recipeno = 0

# Gets all relevant links.
def getlinks(data):
    links = []
    html_links = re.findall("<a.*href=\"(.+?)\"", data) # this regular expression is flawed.
    for link in html_links:
        if link.find(Settings.BASE_SERVER) != -1:
            link = link[:link.find("/", 6)]
        link = Settings.BASE_SERVER + link
        if link.find(Settings.MAIN_BRANCH) != -1 and link not in links:
            links.append(link)
    return links

def removewhitespace(data):
    words = re.findall("(\S*)", data)
    builtstring = ""
    for word in words:
        if word != '':
            builtstring += word + " "
    return builtstring

# Scans and downloads the recipe to a file.
def scanrecipe(data):
    rparser.feed(data)
    if rparser.iscomplete():
        global recipeno
        file = open(Settings.BASE_FILENAME + str(recipeno) + Settings.FILE_EXTENSION, "w", encoding=Settings.DEFAULT_ENCODING)
        recipeno += 1
        ingredients = ""
        method = ""
        for ing in rparser.ingredients:
            ingredients += removewhitespace(ing) + "~"
        for met in rparser.method:
            method += met + "~"
        file.write("Title:" + rparser.title + "\n")
        file.write("Ingredients:" + ingredients + "\n")
        file.write("Total Time:" + rparser.time + "\n")
        file.write("Serves:" + rparser.serves + "\n")
        file.write("Method:" + method + "\n")
        rparser.method = []
        rparser.ingredients = []
        rparser.title = None
        rparser.serves = None
        rparser.time = None
        file.close()

# Downloads the HTML for that page, scans it for a recipe, downloads the links and pushes them to relevant stacks.
def processlink(address):
    processedlinks.append(address)
    try:
        html = network.requestpage(address) # Links already visited are pushed to the main link list
        if html != None:
            links = getlinks(html)
            for link in links:
                if link not in processedlinks and link not in mainlinks:
                    mainlinks.append(link)
            scanrecipe(html)
            print("(#" + str(recipeno) + ") Link processed: " + address)
        else:
            print("(#" + str(recipeno) + ") Link couldn't be processed: " + address)
    except Exception as ex:
        print("(#" + str(recipeno) + ") Error: " + str(ex))

# Calculates the number of links that haven't been visited.
def calculateunvisitedlinks():
    difference = 0
    for link in mainlinks:
        if not link in processedlinks:
            difference += 1
    return difference

def savestate():
    file = open(Settings.SAVE_FILE_NAME, "w")
    file.write("Stack1:#")
    for link in mainlinks:
        file.write("'" + link + "'")
    file.write("#\nStack2:#")
    for link in processedlinks:
        file.write("%" + link + "%")
    file.write("#\nRecipeno:<" + str(recipeno) + ">")
    file.close()

def loadstate():
    global recipeno
    file = open(Settings.SAVE_FILE_NAME, "r")
    contents = file.read()
    stackonelinks = re.findall("'(.+?)'", contents)
    stacktwolinks = re.findall("%(.+?)%", contents)
    recipeno = re.findall("<(.+?)>", contents)
    for link in stackonelinks:
        mainlinks.append(link)
    for link in stacktwolinks:
        processedlinks.append(link)
    recipeno = int(recipeno.pop(0))
    file.close()

def start(loaded):
    linkcount = 0
    if not loaded:
        mainlinks.append(Settings.MAIN_BRANCH)
    while calculateunvisitedlinks() > 0:
        link = mainlinks.pop()
        processlink(link)
        linkcount += 1
        if linkcount == Settings.AUTO_SAVE_INTERVAL:
            linkcount = 0
            savestate()

print("True Blacklight V" + Settings.VERSION)
startstate = input("Load program from save file?(y/n): ").lower()
if startstate == "y":
    print("Loading save file...")
    if loadstate():
        print("Save file loaded successfully")
        print("Starting program...")
        start(True)
    else:
        print("Unable to load save file")
elif startstate == "n":
    print("Starting program...")
    start(False)
