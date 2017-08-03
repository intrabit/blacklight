# Scrapes the HTML for information.
# Louis 15/07/2017 13:32

import recipebot.Settings as settings

class Scraper:
    def __init__(self):
        try:
            file = open(settings.SCRAPE_FILE_PATH, "r")
        except FileNotFoundError | FileExistsError as err:
            pass
