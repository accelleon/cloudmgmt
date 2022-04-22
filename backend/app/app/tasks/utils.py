import asyncio


# Decorator to run async function as sync
def run_sync(func):
    def wrapper(*args, **kwargs):
        loop = asyncio.get_running_loop()
        loop.run_until_complete(func(*args, **kwargs))
        loop.close()

    return wrapper
