import re
import string
import tarfile
from collections import Counter, defaultdict, OrderedDict

from tqdm import tqdm


class Suggest:
    translate_table = dict((ord(char), None) for char in string.punctuation)
    trantab = str.maketrans(string.whitespace, ' ' * len(string.whitespace))

    def __init__(self):
        self.word_popularity = Counter()
        self.combos = defaultdict(list)

        # input_fn = './texts.small.tar.bz2'
        input_fn = './texts.tar.bz2'
        with tarfile.open(input_fn, "r:bz2") as tar:
            for docid, tarinfo in tqdm(enumerate(tar)):
                with tar.extractfile(tarinfo) as inp:
                    words = self.normalization(inp.read().decode('utf8'))
                    self.word_popularity.update(words)

    def normalization(self, text):
        text = text.lower()
        text = re.sub(r"\d+", "", text)  # remove digits
        text = text.translate(self.translate_table)  # remove punctuations
        # TODO: don\'t remove punctuation inside the word
        words = text.translate(self.trantab).split()  # split by whitespaces, remove \n
        return [i for i in words if i.isalpha()]

    def generate_ngrams(self, s: str):
        return [ngr for ngr in [s[:i] for i in range(1, len(s))]]

    def generate_combos(self):

        for word in self.word_popularity:
            ngrams = self.generate_ngrams(word)
            for ngram in ngrams:
                self.combos[ngram].append(word)


suggester = Suggest()
suggester.generate_combos()


def suggest(prefix: str):
    if not prefix or prefix[-1] == ' ':
        return [prefix + i[0] + " "
                for i in suggester.word_popularity.most_common(10)]
    words = prefix.split()
    sgs = suggester.combos[words[-1].lower()][:10]
    base_prefix = " ".join(words[:-1])
    return [base_prefix + " " + i + " " for i in sgs]
    # return ['harry', 'potter', 'harry potter']


def search(query):
    return []
    """
    Каждый документ должен быть описан диктом:
      title - строка, заголовок документа - первая строчка в файле
      link - урл, имя файла в архиве совпадает с названием документа на сайте википедии
      snippet - html, составляется самостоятельно на основе запроса и текста документа

    Пример результата работы функции

    [{'title': 'Harry Potter',
      'link': 'https://simple.wikipedia.org/wiki/Harry_Potter',
      'snippet': '<b>Lorem Ipsum</b> is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry\'s standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. ',
     },
     {'title': 'Таня Гроттер', 
      'link': 'https://simple.wikipedia.org/wiki/Tanya_Grotter', 
      'snippet': '<b>Sed ut perspiciatis</b>, unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam eaque ipsa, quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt, explicabo.',
     }]
    """


if __name__ == '__main__':
    suggester = Suggest()
    suggester.generate_combos()
