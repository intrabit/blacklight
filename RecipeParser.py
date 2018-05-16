from html.parser import HTMLParser
from enum import Enum

websites = {"www.jamieoliver.com" : {
        "Ingredients" : "ingred-list ",
        "Method" : "recipeSteps",
        "Title" : ("h1", "hidden-xs"),
        "Servings" : "recipe-detail serves",
        "Time" : "recipe-detail time"
    }
}

def getfield(attrs, field):
    for t in attrs:
        if t[0] == field:
            return t[1]
    return None

class RecordType(Enum):
    NONE = 1
    INGREDIENTS = 2
    METHOD = 3
    TITLE = 4
    TIME = 5
    SERVES = 6

class RecipeParser(HTMLParser):
    def __init__(self, site):
        HTMLParser.__init__(self)
        self.ingredients = []
        self.method = []
        self.opentag = ""
        self.classes = websites[site]
        self.record = RecordType.NONE
        self.complete = 0

    def iscomplete(self):
        return self.ingredients and self.method and self.title is not None and self.serves is not None and self.time is not None

    def handle_starttag(self, tag, attrs):
        name = getfield(attrs, "class")
        if name is not None:
            if tag == self.classes["Title"][0] and name == self.classes["Title"][1]:
                self.record = RecordType.TITLE
                self.opentag = tag
            elif name == self.classes["Ingredients"]:
                self.record = RecordType.INGREDIENTS
                self.opentag = tag
            elif name == self.classes["Method"]:
                self.record = RecordType.METHOD
                self.opentag = tag
            elif name == self.classes["Servings"]:
                self.record = RecordType.SERVES
                self.opentag = tag
            elif name == self.classes["Time"]:
                self.record = RecordType.TIME
                self.opentag = tag

    def handle_data(self, data):
        if self.record != RecordType.NONE:
            if self.record == RecordType.INGREDIENTS:
                data = data.strip()
                if data != "":
                    self.ingredients.append(data)
            elif self.record == RecordType.METHOD:
                if data.strip() != "":
                    self.method.append(data)
            elif self.record == RecordType.TITLE:
                self.title = data
            elif self.record == RecordType.SERVES:
                self.serves = data.strip()
            elif self.record == RecordType.TIME:
                self.time = data

    def handle_endtag(self, tag):
        if tag == self.opentag:
            self.opentag = None
            self.record = RecordType.NONE
