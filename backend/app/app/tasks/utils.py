import asyncio

loop = None


# Decorator to run async function as sync
def run_sync(func):
    def wrapper(*args, **kwargs):
        global loop
        if loop is None:
            loop = asyncio.get_event_loop()
        return loop.run_until_complete(func(*args, **kwargs))

    return wrapper
