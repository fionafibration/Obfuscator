from math import ceil, log
import marshal
import sys

def encode(num, depth):
    if num == 0:
        return "_ - _"
    if num <= 8:
        return "_" * (num + 1)
    return "(" + numconvert(num, depth + 1) + ")"


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

        block_num = 0
        block = block[::-1]

        for i, char in enumerate(block):
            block_num += char * (256 ** i)

        block_nums.append(block_num)

    return block_nums


def convert(instring, depth=0):
    blocks = get_blocks(instring, block_size=16)
    for i, block in enumerate(blocks):
        converted = numconvert(block)
        yield converted


def main():
    import hashlib
    code_bytes = marshal.dumps(compile(sys.stdin.read(), '<string>', 'exec'))
    sys.stderr.write(hashlib.sha256(code_bytes).hexdigest())
    finalcodedata = ', '.join(convert(code_bytes))
    sys.stdout.write('''__, ___, ____, _____, ______, _______, ________, _________ = range(1, 9)\n_ = [''')
    sys.stdout.write(finalcodedata)
    sys.stdout.write(''']\n____________ = lambda f, k: b''.join([f(f, n)[::-1] for n in k])\n_____________ = lambda f, n: bytes([n % 256]) + f(f, n // 256) if n else b""''')

if __name__ == '__main__':
    main()
