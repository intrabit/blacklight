# Scrapes the HTML for information.

import recipebot.Settings as settings

class Scraper:
    def __init__(self):
        try:
            file = open(settings.SCRAPE_FILE_PATH, "r")
        except FileNotFoundError | FileExistsError as err:
            pass
