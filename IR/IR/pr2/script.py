import string
import codecs

KEYBOARD_RU_EN = {'ё': '`', 'Ё': '~', '"': '@', '№': '#', ';': '$', ':': '^', '?': '&', 'й': 'q', 'Й': 'Q', 'ц': 'w', 'Ц': 'W', 'У': 'E', 'у': 'e', 'К': 'R', 'к': 'r', 'Е': 'T', 'е': 't', 'Н': 'Y', 'н': 'y', 'Г': 'U', 'г': 'u', 'Ш': 'I', 'ш': 'i', 'Щ': 'O', 'щ': 'o', 'З': 'P', 'з': 'p', 'Х': '{', 'х': '[', 'ъ': ']', 'Ъ': '}', '/': '|', '\\': '\\', 'Ф': 'A', 'ф': 'a', 'Ы': 'S', 'ы': 's', 'В': 'D', 'в': 'd', 'А': 'F', 'а': 'f', 'П': 'G', 'п': 'g', 'Р': 'H', 'р': 'h', 'О': 'J', 'о': 'j', 'Л': 'K', 'л': 'k', 'Д': 'L', 'д': 'l', 'Ж': ':', 'ж': ';', 'Э': '"', 'э': '\'', 'Я': 'Z', 'я': 'z', 'Ч': 'X', 'ч': 'x', 'С': 'C', 'с': 'c', 'М': 'V', 'м': 'v', 'И': 'B', 'и': 'b', 'Т': 'N', 'т': 'n', 'Ь': 'M', 'ь': 'm', 'Б': '<', 'б': ',', 'Ю': '>', 'ю': '.', ',': '?', '.': '/'}
KEYBOARD_EN_RU = {'`': 'ё', '~': 'Ё', '@': '"', '#': '№', '$': ';', '^': ':', '&': '?', 'q': 'й', 'Q': 'Й', 'w': 'ц', 'W': 'Ц', 'E': 'У', 'e': 'у', 'R': 'К', 'r': 'к', 'T': 'Е', 't': 'е', 'Y': 'Н', 'y': 'н', 'U': 'Г', 'u': 'г', 'I': 'Ш', 'i': 'ш', 'O': 'Щ', 'o': 'щ', 'P': 'З', 'p': 'з', '{': 'Х', '[': 'х', ']': 'ъ', '}': 'Ъ', '|': '/', '\\': '\\', 'A': 'Ф', 'a': 'ф', 'S': 'Ы', 's': 'ы', 'D': 'В', 'd': 'в', 'F': 'А', 'f': 'а', 'G': 'П', 'g': 'п', 'H': 'Р', 'h': 'р', 'J': 'О', 'j': 'о', 'K': 'Л', 'k': 'л', 'L': 'Д', 'l': 'д', ':': 'Ж', ';': 'ж', '"': 'Э', '\'': 'э', 'Z': 'Я', 'z': 'я', 'X': 'Ч', 'x': 'ч', 'C': 'С', 'c': 'с', 'V': 'М', 'v': 'м', 'B': 'И', 'b': 'и', 'N': 'Т', 'n': 'т', 'M': 'Ь', 'm': 'ь', '<': 'Б', ',': 'б', '>': 'Ю', '.': 'ю', '?': ',', '/': '.'}


def translate_kb(s, kb):
    result = ''
    for ch in s:
        if ch in kb:
            result += kb[ch]
        else:
            result += ch
    return result


def translate(s):
    rus = eng = 0
    for ch in s:
        if ch.isalpha():
            if ch in string.ascii_letters:
                eng += 1
            else:
                rus += 1
    if eng > rus:
        return translate_kb(s, KEYBOARD_EN_RU)
    return translate_kb(s, KEYBOARD_RU_EN)


# единственный словарь который можно использовать
voc = set()
with codecs.open('./learn.txt', 'r', 'utf8') as f:
    for line in f:
        for word in line.rstrip().split():
            voc.add(word)

print(len(voc))


def corrector(query):
    words = query.split()
    for word in words:
        if word not in voc:
            return translate(query)
    return query


with codecs.open('./test_result.txt', 'r', 'utf8') as f:
    err = 0
    ok = 0
    for line in f:
        query, result = line.rstrip().split('\t')
        predict = corrector(query)
        if predict != result:
            err += 1
        else:
            ok += 1
    print('Ошибок: %s/%s' % (err, err+ok))

    if err < 100:
        print('Зачёт!')
    else:
        print('Стоит еще немножко поработать...')