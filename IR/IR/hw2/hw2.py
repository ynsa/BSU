import bz2
import csv
import hashlib
import string
import tarfile
from collections import defaultdict, Counter, OrderedDict


def filte_cnt(counter: Counter, min_value: int) -> Counter:
    copy_counter = counter.copy()
    for key, cnts in list(copy_counter.items()):
        if cnts < min_value:
            del copy_counter[key]
    return copy_counter


all_docs_content = {}
with tarfile.open('./collection.tar.bz2', 'r:bz2') as tf:
    for ti in tf:
        byte_content = tf.extractfile(ti).read()
        all_docs_content[ti.name] = byte_content


def force_decode(string, codecs=('utf8', 'cp1252')):
    for i in codecs:
        try:
            return string.decode(i)
        except UnicodeDecodeError:
            pass

    print(f"cannot decode url {string}")


def force_encode(string, codecs=('utf8', 'cp1252')):
    for i in codecs:
        try:
            return string.encode(i)
        except UnicodeDecodeError:
            pass

    print(f"cannot encode url {string}")


print(f'Amount of docs: {len(all_docs_content)}.')

all_docs_content = {k: force_decode(s) for k, s in all_docs_content.items()}
trantab = str.maketrans(string.whitespace, ' ' * len(string.whitespace))
all_docs_content = {k: ' '.join(s.translate(trantab).split()) for k, s in all_docs_content.items()}
hashs = {}

for k, v in all_docs_content.items():
    hashs[k] = hashlib.blake2b(force_encode(v)).hexdigest()


print(f'Amount of hashs: {len(hashs)}.')
hash_file = defaultdict(list)
for file, hash_f in hashs.items():
    hash_file[hash_f].append(file)
print(f'Len hash_file = {len(hash_file)}')
hash_counter = Counter(hashs.values())

duples_counter = filte_cnt(hash_counter, 2)
print(f'The biggest group contains {duples_counter.most_common(1)[0][1]} files.')
print(f'The smallest group contains {duples_counter.most_common()[-1][1]} file.')
print(f'Total amount of duplicated groups: {len(duples_counter)}.')
print(f'Amount of duples: {sum(duples_counter.values()) - len(duples_counter)}.')
print(f'Average amount of duples: {sum(duples_counter.values()) / len(duples_counter)}.\n')


def generate_identical_ground_truth():

    new_ground_truth = OrderedDict()
    with bz2.open('./ground_truth.tsv.bz2', 'rt') as tf:
        tsvreader = csv.reader(tf, delimiter="\t")
        small_count = -1
        i = 0
        removed_files = 0
        counter = 0
        for row in tsvreader:
            counter += 1

            if small_count > -1:
                if not small_count:
                    break
                small_count -= 1
            hash_f = hashs[row[0]]
            new_ground_truth[row[0]] = []
            for file_info in row[1:]:
                file, info = file_info.split('=')
                if file in hash_file[hash_f]:
                    assert info == '1.0'
                else:
                    new_ground_truth[row[0]].append(file_info)
        print(f'Minimum duplicate score for full duples = 1.0.')
        print(f'Save space for {removed_files} files.')
        print(f'New ground truth contains {len(new_ground_truth.keys())} files.')
        print(f'Total amount in file was: {counter}.')

    with bz2.open('./identical_ground_truth.tsv.bz2', 'wt', newline='') as tf:
        tsvwriter = csv.writer(tf, delimiter="\t")
        rows = []
        for file, duples in new_ground_truth.items():
            ftw = [file] + duples
            rows.append(ftw)
        tsvwriter.writerows(rows)


# generate_identical_ground_truth()

class MinHash:

    def __init__(self, all_docs_content, files, k=1):
        self.all_docs_content = all_docs_content
        self.files = files
        self.k = k
        self.hashs = {}
        self.hash_file = [defaultdict(list) for i in range(k)]

    def hash_func(self, k, data):
        hs = hashlib.md5(force_encode(data)).hexdigest()
        hs = int(hs, 16)
        # hs = hash(data)
        # hs = hashlib.blake2b(force_encode(data)).hexdigest()
        return hs * (200 - (k + 1) * 13) + (k + 1) % 255

    def generate_ngrams(self, s: str, n: int):
        s = s.lower()
        tokens = [token for token in s.split(" ") if token != ""]
        ngrams = zip(*[tokens[i:] for i in range(n)])
        return [" ".join(ngram) for ngram in ngrams]

    def min_hash(self, n_grams: list):
        hashs = [[] for i in range(self.k)]
        for n_gram in n_grams:
            for i in range(self.k):
                hashs[i].append(self.hash_func(i, ' '.join(n_gram)))
        hashs = [min(lst) for lst in hashs]
        return hashs

    def generate_hashs(self):
        for i, file in enumerate(self.files):
            content = all_docs_content[file]
            n_gram = self.generate_ngrams(content, 4)
            file_min_hash = self.min_hash(n_gram)
            for i in range(self.k):
                self.hash_file[i][file_min_hash[i]].append(file)
            self.hashs[file] = file_min_hash

    def duples_count(self):
        print('-' * 10, f'\nk={self.k}')
        rows = []
        for file in self.files:
            common = []
            for i in range(self.k):
                common.extend(self.hash_file[i][self.hashs[file][i]])
            counter = Counter(common)
            rows.append([file] + [f'{i}={val / self.k}' for i, val in counter.items() if i != file])

        with bz2.open(f'./minhash_ground_truth_{self.k}.tsv.bz2', 'wt',
                      newline='') as tf:
            tsvwriter = csv.writer(tf, delimiter="\t")
            tsvwriter.writerows(rows)
        with open(f'./minhash_ground_truth_{self.k}.txt', 'w', newline='') as tf:
            tsvwriter = csv.writer(tf, delimiter="\t")
            tsvwriter.writerows(rows)

    def execute(self):
        self.generate_hashs()
        self.duples_count()


files = [x[0] for key, x in hash_file.items()]
MinHash(all_docs_content=all_docs_content, files=files, k=10).execute()
