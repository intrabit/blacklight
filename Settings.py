# This file defines all settings for Blacklight.

LINK_BUFFER_SIZE = 200  # The buffer that holds the links to be crawled.
MAX_THREADS = 4
FAILED_THREAD_ABORT = 2  # The number of threads that have to fail before the program aborts.
VERSION = "0.1.0"
CONNECTION_TIMEOUT = 2
RESPONSE_BUFFER_SIZE = 4096  # The size of the buffer that holds the server response.
DEFAULT_ENCODING = "utf-8"
SCRAPE_FILE_PATH = "Ingredients.scr"  # The name of the scrape file used to determine what data to scrape from the HTML.

#  TODO: In later versions use a byte array to store incoming data. Will be faster.
#  TODO: Finish scraper.
