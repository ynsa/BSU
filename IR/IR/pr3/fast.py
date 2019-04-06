import bz2
from collections import Counter

ranks = {}
global_links = {}
prob_any = {}
with bz2.open('./links.full.txt.bz2', 'rt', encoding='utf8') as f:
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
total_sum = total_pages * 1
unlinked_ranks = 0

for x in global_links:
    if not len(global_links[x]):
        unlinked_ranks += 1

stop = False
delta = 0.7
i = 0
new_ranks = {}
prob_any = 1 / total_pages

while not stop:
    print('-' * 4, i, '-'*4)
    new_ranks = ranks.copy()

    for x in new_ranks:
        new_ranks[x] = prob_any * ((1 - delta) * total_sum + delta * unlinked_ranks)

    iter_total_sum = 0
    for x in ranks:
        x_links = global_links[x]
        for y in x_links:
            new_ranks[y] += ranks[x] * delta * x_links[y]
        # rank[x] * (prob_any * prob_go + prob_link * prob_go)

    stop = True
    unlinked_ranks = 0
    maxx = 0
    for x in new_ranks:
        if not len(global_links[x]):
            unlinked_ranks += new_ranks[x]
        iter_total_sum += new_ranks[x]
        maxx = maxx if maxx > abs(ranks[x] - new_ranks[x]) else abs(ranks[x] - new_ranks[x])
        if abs(ranks[x] - new_ranks[x]) > pow(10, -5):
            stop = False
    print('Max difference through iteration: {:.8f}'.format(maxx))
    if abs(iter_total_sum - total_sum) > pow(10, -5):
        print(f'{i}: {total_sum} -> {iter_total_sum}')
        raise ValueError('Not correct')
    ranks = new_ranks.copy()
    i += 1


h = list(new_ranks.items())
h = sorted(h, key=lambda x: x[1], reverse=True)
for i in h[:10]:
    print(f'{i[0]}: {i[1]}')


