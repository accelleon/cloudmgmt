import asyncio


# Decorator to run async function as sync
def run_sync(func):
    def wrapper(*args, **kwargs):
        # TODO: Gotta be a less hacky way to do this
        # get_event_loop() doesn't work here for multiple functions
        # because of a race condition where we close the loop after the
        # next task grabs it, but before it finishes
        loop = asyncio.new_event_loop()
        loop.run_until_complete(func(*args, **kwargs))
        loop.close()

    return wrapper
