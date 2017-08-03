# Blacklight Web Bot Version 0.1.0
# Written by Louis Kennedy

import queue
from recipebot.Worker import Worker
import recipebot.Settings as settings

def execute():
    print("Blacklight starting...")
    print("Blacklight version " + settings.VERSION)
    links = queue.Queue(maxsize=settings.LINK_BUFFER_SIZE)
    failedthreads = 0
    address = input("Enter starting website: ")
    links.put(item=address, block=True)
    links.task_done()
    for threads in range(1, settings.MAX_THREADS + 1):
        if failedthreads <= settings.FAILED_THREAD_ABORT:
            try:
                thread = Worker(links)
                thread.daemon = False
                thread.start()
                print("Worker #" + str(threads) + " starting.")
            except:
                print("\aWorker #" + str(threads) + " failed to start.")
                failedthreads += 1
        else:
            print("More workers failed than permitted. Aborting program.")
            return

execute()