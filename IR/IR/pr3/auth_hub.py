import bz2
from collections import Counter
from math import log10

global_links = {}
global_sources = {}
pages = []
auth = {}
hub = {}

with bz2.open('./links.mistery.txt.bz2', 'rt', encoding='utf8') as f:
    for line in f:
        links = line.rstrip().split('\t')
        x = links[0]
        pages.append(x)
        auth[x] = 1
        hub[x] = 1
        global_sources[x] = []

        links_count = len(links) - 1
        x_set = Counter(links[1:])
        temp_links = []
        for link in x_set:
            temp_links.append(link)
            y_sources = global_sources.get(link, [])
            y_sources.append(x)
            global_sources[link] = y_sources

        global_links[x] = temp_links


def normalized_sum(auth):
    return sum([pow(auth[y], 2) for y in auth])


total_pages = len(global_links)
total_sum = sum([pow(auth[y], 2) for y in auth])

stop = False
i = 0
while not stop:
    print('-' * 4, i, '-'*4)

    new_auth = {}
    new_hub = {}

    for x in pages:
        new_auth[x] = sum([hub[y] for y in global_sources[x]]) + 1
        new_hub[x] = sum([auth[y] for y in global_links[x]]) + 1

    stop = True
    iter_total_sum = 0
    maxx = 0

    for x in pages:
        # new_auth[x] = log10(new_auth[x])
        # new_hub[x] = log10(new_hub[x])
        new_auth[x] = new_auth[x] / 2000
        new_hub[x] = new_hub[x] / 2000

        maxx = maxx if maxx > abs(auth[x] - new_auth[x]) else abs(auth[x] - new_auth[x])
        if abs(auth[x] - new_auth[x]) > pow(10, -5):
            stop = False

    print('Max difference through iteration: {:.8f}'.format(maxx))

    auth = new_auth.copy()
    hub = new_hub.copy()
    i += 1


h = list(auth.items())
h = sorted(h, key=lambda x: x[1], reverse=True)
for i in h[:10]:
    print(f'{i[0]}: {i[1]}')
