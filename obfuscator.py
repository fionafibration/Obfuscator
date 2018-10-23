from math import ceil, log
import marshal
import sys

def encode(num, depth):
    if num == 0:
        return "__ - __"
    if num <= 8:
        return "_" * (num + 1)
    return "(" + numconvert(num, depth + 1) + ")"

# Ben Kurtovic's bitshift conversion algorithm: https://benkurtovic.com/2014/06/01/obfuscating-hello-world.html
def numconvert(num, depth=0):
    result = ""
    while num:
        base = shift = 0
        diff = num
        span = int(ceil(log(abs(num), 1.5))) + (16 >> depth)
        for test_base in range(span):
            for test_shift in range(span):
                test_diff = abs(num) - (test_base << test_shift)
                if abs(test_diff) < abs(diff):
                    diff = test_diff
                    base = test_base
                    shift = test_shift
        if result:
            result += " + " if num > 0 else " - "
        elif num < 0:
            base = -base
        if shift == 0:
            result += encode(base, depth)
        else:
            result += "(%s << %s)" % (encode(base, depth),
                                      encode(shift, depth))
        num = diff if num > 0 else -diff
    return result


def get_blocks(message, block_size=256):
    block_nums = []

    for block in [message[i:i + block_size] for i in range(0, len(message), block_size)]:
        block = b'\x80' + block + b'\x80'
        block_num = 0
        block = block

        for i, char in enumerate(block):
            block_num += char * (256 ** i)

        block_nums.append(block_num)

    return block_nums


def convert(instring):
    blocks = get_blocks(instring, block_size=16)
    return [numconvert(block) for block in blocks]


def main():
    code_bytes = marshal.dumps(compile(sys.stdin.read(), '<string>', 'exec'), 2)
    encoded = ', '.join(convert(code_bytes))
    # Range call is obfuscated based on Ben Kurtovic's obfuscated hello world. https://benkurtovic.com/2014/06/01/obfuscating-hello-world.html
    sys.stdout.write('''(lambda __, ___, ____, _____, ______, _______, ________, _________, __________: getattr(__import__("\\x62\\x75\\x69\\x6c\\x74\\x69\\x6e\\x73"), "\\x65\\x78\\x65\\x63")(getattr(__import__("\\x6d\\x61\\x72\\x73\\x68\\x61\\x6c"), "\\x6c\\x6f\\x61\\x64\\x73")((lambda _________________: getattr(b'', "\\x6a\\x6f\\x69\\x6e")([(lambda _______________, ________________: getattr(__import__("\\x62\\x75\\x69\\x6c\\x74\\x69\\x6e\\x73"), "\\x62\\x79\\x74\\x65\\x73")([________________ % (__ << _________)]) + _______________(_______________, ________________ // (__ << _________)) if ________________ else b"")((lambda _______________, ________________: getattr(__import__("\\x62\\x75\\x69\\x6c\\x74\\x69\\x6e\\x73"), "\\x62\\x79\\x74\\x65\\x73")([________________ % (__ << _________)]) + _______________(_______________, ________________ // (__ << _________)) if ________________ else b""), ___________________________)[__:__ - ___] for ___________________________ in _________________]))([''')
    sys.stdout.write(encoded)
    sys.stdout.write(''']))))(*(lambda _, __, ___: _(_, __, ___))((lambda _, __, ___: [__(___[(lambda: _).__code__.co_nlocals])] +_(_, __, ___[(lambda _: _).__code__.co_nlocals:]) if ___ else []), lambda _: _.__code__.co_argcount, (lambda _: _, lambda _, __: _, lambda _, __, ___: _, lambda _, __, ___, ____: _, lambda _, __, ___, ____, _____: _, lambda _, __, ___, ____, _____, ______: _, lambda _, __, ___, ____, _____, ______, _______: _, lambda _, __, ___, ____, _____, ______, _______, ________: _, lambda _, __, ___, ____, _____, ______, _______, ________, _________: _)))''')


if __name__ == '__main__':
    main()