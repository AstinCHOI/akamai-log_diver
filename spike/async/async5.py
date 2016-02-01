import timeit
from urllib.request import urlopen

urls = ['https://google.com', 'https://apple.com']
start = timeit.default_timer()

for url in urls:
    print('Start', url)
    urlopen(url)
    print('Done', url)

duration = timeit.default_timer() - start 

# Start https://google.com
# Done https://google.com
# Start https://apple.com
# Done https://apple.com