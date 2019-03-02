import bz2
from collections import Counter

ranks = {}
global_links = {}
prob_random = {}
with bz2.open('./links.small.txt.bz2', 'rt', encoding='utf8') as f:
    for line in f:
        links = line.rstrip().split('\t')
        x = links[0]
        ranks.update({x: 1})
        links_count = len(links) - 1
        x_set = Counter(links[1:])
        temp_links = {}
        for link in x_set:
            temp_links.update({link: x_set[link] / links_count})

        global_links.update({x: temp_links})

total_pages = len(global_links)
for x in global_links:
    print(f'Page: {x}')
    lnk = global_links[x]
    prob_random[x] = 1 / (total_pages - len(lnk))
    print(' ' * 2, f'Random page probability: {prob_random[x]}')
    for y in lnk:
        print(' ' * 4, f'{y} : {lnk[y]}')
        # for y in links[1:]:
            # link from `x` to `y`

stop = False
delta = 0.7
i = 0
# while i != 3:
new_ranks = {}
while not stop:
    print('-' * 4, i, '-'*4)
    new_ranks = ranks.copy()
    for x in new_ranks:
        new_ranks[x] = 0

    for x in ranks:
        x_links = global_links[x]
        pr_rand = 1 - delta if len(x_links) else 1
        for y in ranks:
            new_ranks[y] += pr_rand * prob_random[x]
            if y in x_links:
                new_ranks[y] += ranks[x] * delta * x_links[y]

    stop = True
    for x in ranks:
        if abs(ranks[x] - new_ranks[x]) > pow(10, -5):
            print('{}: {:.5f} -> {:.5f}'.format(x, ranks[x], new_ranks[x]))
            stop = False
    ranks = new_ranks.copy()
    i += 1


h = list(new_ranks.items())
h = sorted(h, key=lambda x: x[1], reverse=True)
for i in h[:10]:
    print(f'{i[0]}: {i[1]}')


