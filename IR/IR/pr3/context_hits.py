import bz2
from collections import Counter
from math import log10


def authhub(pages, global_sources, global_links):
    auth = {x: 1 for x in pages}
    hub = {x: 1 for x in pages}

    stop = False
    i = 0
    while not stop:
        print('\t', '-' * 4, i, '-' * 4)

        new_auth = {}
        new_hub = {}

        for x in pages:
            new_auth[x] = sum([hub[y] for y in global_sources[x]]) + 1
            new_hub[x] = sum([auth[y] for y in global_links[x]]) + 1

        stop = True
        maxx = 0

        for x in pages:
            # new_auth[x] = log10(new_auth[x])
            # new_hub[x] = log10(new_hub[x])
            new_auth[x] = new_auth[x] / 2000
            new_hub[x] = new_hub[x] / 2000

            maxx = maxx if maxx > abs(auth[x] - new_auth[x]) else abs(
                auth[x] - new_auth[x])
            if abs(auth[x] - new_auth[x]) > pow(10, -5):
                stop = False

        print('\tMax difference through iteration: {:.8f}'.format(maxx))

        auth = new_auth.copy()
        hub = new_hub.copy()
        i += 1

    h = list(auth.items())
    h = sorted(h, key=lambda x: x[1], reverse=True)
    for i in h[:10]:
        print(f'\t\t{i[0]}: {i[1]}')


global_links = {}
global_sources = {}

with bz2.open('./links.full.txt.bz2', 'rt', encoding='utf8') as f:
    for line in f:
        links = line.rstrip().split('\t')
        x = links[0]
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

root_sets = []
with open('./relevant.txt', 'rt', encoding='utf8') as f:
    for line in f:
        root_sets.append(set())
        root_sets[-1].update(line.rstrip().split('\t'))


base_sets = []
for i, root_set in enumerate(root_sets):
    base_sets.append(set())
    for x in root_set:
        base_sets[i].update(global_links[x])
    set_len = len(base_sets[i])
    new_set_len = 0
    new_base_set = set()
    while new_set_len != set_len:
        new_base_set = set()
        set_len = new_set_len
        united = base_sets[i].union(root_set)
        for y in base_sets[i]:
            if not any([link not in united for link in global_links[y]]):
                new_base_set.add(y)
        new_set_len = len(new_base_set)
    base_sets[i] = new_base_set.copy()


for i, root_set in enumerate(root_sets):
    print(f'Root set {i + 1}:\n')
    for x in root_set:
        print(f'\t{x}')
    print(f'Base set {i + 1}:\n')
    for x in base_sets[i]:
        print(f'\t{x}')
    print('\n', '-' * 10, '\n')


for i in range(len(root_sets)):
    links = root_sets[i].union(base_sets[i])
    gl_links = {x: global_links[x] for x in links}
    gl_sources = {x: global_sources[x] for x in links}
    for x in links:
        new_links = []
        for y in gl_links[x]:
            if y in links:
                new_links.append(y)
        gl_links[x] = new_links
        new_links = []
        for y in gl_sources[x]:
            if y in links:
                new_links.append(y)
        gl_sources[x] = new_links

    print(f'Query set {i}:\n')
    authhub(links, gl_sources, gl_links)
    print('-' * 10, '\n')
