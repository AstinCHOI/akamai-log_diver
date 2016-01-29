import aiohttp
import asyncio
import timeit

@asyncio.coroutine
def fetch(url):
    print('Start', url)
    req = yield from aiohttp.request('GET', url)
    print('Done', url)

@asyncio.coroutine
def fetch_all(urls):
    fetches = [asyncio.Task(fetch(url)) for url in urls]
    yield from asyncio.gather(*fetches)

urls = ['https://google.com', 'https://apple.com', 'https://ubit.info', 'https://github.com/ssut']

start = timeit.default_timer()
asyncio.get_event_loop().run_until_complete(fetch_all(urls))
duration = timeit.default_timer() - start

# Start https://google.com
# Start https://apple.com
# Start https://ubit.info
# Start https://github.com/ssut
# Done https://ubit.info
# Done http://b.ssut.me
# Done https://google.com
# Done https://apple.com
# Done https://github.com/ssut
# => duration = 0.9832467940016068