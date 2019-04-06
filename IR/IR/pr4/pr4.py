import bz2
import io
import random
import tarfile
from collections import defaultdict

from tqdm import tqdm
import struct


# example coder 1
class simple_text_coder:
    def write(out_stream, x_list):
        for x in x_list:
            out_stream.write(str(x).encode('utf8'))
            out_stream.write(b'\t')

    def read(inp_stream):
        return list(map(int, inp_stream.read().split()))


output = io.BytesIO()
simple_text_coder.write(output, [1, 2, 3, 300])
print(output.getvalue())


# example coder 2

class simple_4byte_coder:
    def write(out_stream, x_list):
        for x in x_list:
            out_stream.write(struct.pack('I', x))

    def read(inp_stream):
        res = []
        while True:
            data = inp_stream.read(struct.calcsize('I'))
            if len(data) == 0:
                break
            res.append(struct.unpack('I', data)[0])
        return res


output = io.BytesIO()
simple_4byte_coder.write(output, [1, 2, 3, 300])
print(output.getvalue())


# code here
class varint_coder:
    @classmethod
    def write(cls, out_stream, x_list, **kwargs):
        for x in x_list:
            x_write = x & 127
            flag = True
            while flag:
                x >>= 7
                flag = True if x else False
                out_stream.write(struct.pack('B', x_write | (128 if flag else 0)))
                x_write = x & 127

    @classmethod
    def read(cls, inp_stream: io.BytesIO, **kwargs):
        res = []
        x = 0
        shift = 0
        while True:
            data = inp_stream.read(struct.calcsize('B'))
            if len(data) == 0:
                break
            data = struct.unpack('B', data)[0]
            x |= ((data & 127) << shift)
            if not (data & 128):
                res.append(x)
                x = shift = 0
            else:
                shift += 7

        return res


class bz2_coder:
    @classmethod
    def write(cls, out_stream, x_list, **kwargs):
        output = io.BytesIO()
        varint_coder.write(output, x_list)
        x_bytes = output.getvalue()
        compr = bz2.compress(x_bytes, compresslevel=1)
        out_stream.write(compr)

    @classmethod
    def read(cls, inp_stream: io.BytesIO, **kwargs):
        decompr = bz2.decompress(inp_stream.getvalue())
        input = io.BytesIO(decompr)
        return varint_coder.read(input)


class delta_coder:
    @classmethod
    def write(cls, out_stream, x_list, main_coder=varint_coder, **kwargs):
        for i, x in enumerate(x_list):
            if not i:
                xs_write = [x]
            else:
                xs_write.append(x - x_list[i - 1] - 1)
        main_coder.write(out_stream, xs_write)

    @classmethod
    def read(cls, inp_stream: io.BytesIO, main_coder=varint_coder, **kwargs):
        x_list = main_coder.read(inp_stream)
        for i, x in enumerate(x_list):
            if not i:
                xs_write = [x]
            else:
                xs_write.append(x + xs_write[i - 1] + 1)
        return xs_write


def simple_test_coder(coder, test_arr, coder_kwargs={}):
    output = io.BytesIO()
    coder.write(output, test_arr, **coder_kwargs)
    print(output.getvalue())
    print(f'Len: {len(output.getvalue())}')
    output_bytes = output.getvalue()
    input = io.BytesIO(output_bytes)
    res = coder.read(input, **coder_kwargs)
    print(res)
    assert res == test_arr
    print('-'*30)


test_arr = [0, 1, 2, 3, 22, 28, 38, 300]
simple_test_coder(varint_coder, test_arr)
simple_test_coder(delta_coder, test_arr)
simple_test_coder(bz2_coder, test_arr)
simple_test_coder(delta_coder, test_arr, {'main_coder': bz2_coder})


# test engine
def test_coder_single(coder, x, debug=False):
    output = io.BytesIO()
    coder.write(output, x)
    output_bytes = output.getvalue()
    input = io.BytesIO(output_bytes)
    y = coder.read(input)
    if x != y or debug:
        print('%s -> %s -> %s' % (x, output_bytes, y))
    return len(output_bytes)


def test_coder(coder, debug):
    total_size = 0.0

    test_range = list(range(20000) if not debug else range(0, 300, 29))

    # test single ints
    for x in test_range:
        total_size += test_coder_single(coder, [x], debug) / (x + 1)
    print('Done! Size: %f (smaller is better)' % total_size)

    # test list of ints
    sample_max_size = 5
    for i in range(len(test_range)):
        sample_size = random.randint(1, sample_max_size)
        x = sorted(random.sample(test_range, sample_size))
        total_size += test_coder_single(coder, x, debug)
    print('Done! Size: %f (smaller is better)' % total_size)


# test_coder(simple_text_coder, False)
# test_coder(simple_4byte_coder, False)
test_coder(varint_coder, False)
test_coder(delta_coder, False)
test_coder(bz2_coder, False)


posting_list = defaultdict(set)

# with tarfile.open("texts.norm.tar.bz2", "r:bz2") as tar:
with tarfile.open("texts.small.norm.tar.bz2", "r:bz2") as tar:
    for docid, tarinfo in tqdm(enumerate(tar)):
        with tar.extractfile(tarinfo) as inp:
            for term in inp.read().decode('utf8').split():
                posting_list[term].add(docid)


posting_list = {x: sorted(posting_list[x]) for x in posting_list}

len_initial = 4 * sum([len(x) for x in posting_list.values()])
print(f'Without optimization: {len_initial}.')


def codered(coder, posting_list, len_initial, coder_kwargs={}):
    """Compress lists of docids per term in posting_list. Check profit."""

    len_post = 0
    for x in posting_list:
        output = io.BytesIO()
        coder.write(output, posting_list[x], **coder_kwargs)
        len_post += len(output.getvalue())
    coder_name = coder.__name__
    additional_coder = coder_kwargs.get('main_coder', '')
    if additional_coder:
        coder_name += f' and {additional_coder.__name__}'
    print(f'With {coder_name}: {len_post}.\n\t'
          f'Profit: {int((1 - len_post / len_initial) * 100)}%')


codered(varint_coder, posting_list, len_initial)
codered(delta_coder, posting_list, len_initial, {'main_coder': varint_coder})
codered(bz2_coder, posting_list, len_initial)
codered(delta_coder, posting_list, len_initial, {'main_coder': bz2_coder})
