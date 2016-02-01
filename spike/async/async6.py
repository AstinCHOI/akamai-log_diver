import timeit
from concurrent.futures import ThreadPoolExecutor
from urllib.request import urlopen

urls = ['https://google.com', 'https://apple.com', 'https://ubit.info', 'https://github.com/ssut']

def fetch(url):
    print('Start', url)
    urlopen(url)
    print('Done', url)

start = timeit.default_timer()
with ThreadPoolExecutor(max_workers=5) as executor:
    for url in urls:
        executor.submit(fetch, url)

duration = timeit.default_timer() - start


# Start https://google.com
# Start https://apple.com
# Start https://ubit.info
# Start https://github.com/ssut
# Done https://ubit.info
# Done https://google.com
# Done https://apple.com
# Done https://github.com/ssut
# => duration = 0.9867028829976334