# Settings file.

BASE_SERVER = "www.jamieoliver.com"
MAIN_BRANCH = BASE_SERVER + "/recipes/"
BASE_FILENAME = "recipes/recipe_"
SAVE_FILE_NAME = "autosave.bsf"
FILE_EXTENSION = ".rcp"
SOCKET_TIMEOUT = 5
ENCRYPTED = True
DEFAULT_ENCODING = "utf-8"
MAX_RETRIES = 3
RESPONSE_BUFFER_SIZE = 1049
VERSION = "0.01"
AUTO_SAVE_INTERVAL = 5

# Auto Save:
# Every X links, the program saves the state of the stacks and the recipeno to a save file
# so if there's a crash the program can be loaded from a previous position.
