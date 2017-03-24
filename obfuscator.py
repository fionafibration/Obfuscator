import base64, zlib
from math import ceil, log


prefix = """__, ___, ____, _____, ______, _______, ________, _________ = getattr(__import__("builtins"), "range")(1, 9)
__________ = """
suffix = """
getattr(__import__("random"), "seed")((((______ << ___) + __) << __))
________________ = getattr(__import__("builtins"), "list")(getattr(__import__("string"), "ascii_lowercase") + getattr(__import__("string"), "digits"))
getattr(__import__("random"), "shuffle")(________________)
_ = "".join(________________)
___________ = lambda f, n: f(f, n)
____________ = lambda f, n: chr(n % _____________) + f(f, n // _____________) if n else ""
_____________ = (__ << _________)
______________ = ___________(____________, __________)
_______________ = getattr(__import__(_[34] + _[15] + _[14] + _[12] + _[5] + _[14] + _[22] + _[23]), _[30] + _[27] + _[20] + _[12])(______________)
getattr(__import__(_[34] + _[15] + _[14] + _[12] + _[5] + _[14] + _[22] + _[23]), _[30] + _[27] + _[20] + _[12])(getattr(__import__(_[34] + _[15] + _[14] + _[12] + _[5] + _[14] + _[22] + _[23]), _[24] + _[31] + _[1] + _[32] + _[14] + _[12] + _[30])(getattr(__import__(_[7] + _[12] + _[14] + _[34]), _[28] + _[30] + _[24] + _[31] + _[1] + _[32] + _[33] + _[30] + _[23] + _[23])(getattr(__import__(_[34] + _[20] + _[23] + _[30] + _[4] + _[6]), _[34] + _[4] + _[6] + _[28] + _[30] + _[24] + _[31] + _[28] + _[30])(_______________)), "<" + _[23] + _[5] + _[33] + _[14] + _[22] + _[18] + ">", _[30] + _[29] + _[30] + _[24]))"""


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


def convert(instring, depth=0):
    liststr = list(instring)
    codes = []
    for c in liststr:
        codes.append(ord(str(c)))
    outnum = sum(codes[i] * 256 ** i for i in range(len(codes)))
    return numconvert(outnum, depth)


def main():
    inputfile = input("What would you like the input file to be?\n>>>")
    good = False
    while good != True:
        try:
            inputfileObj = open(inputfile, 'r')
            good = True
        except:
            inputfile = input("Please enter a valid filename.\n>>>")	
    outputfile = input("What would you like the output file to be?\n>>>")
    good = False
    while good != True:
        try:
            outputfileObj = open(outputfile, 'w')
            good = True
        except:
            inputfile = input("Please enter a valid filename.\n>>>")
    inputcode = base64.b64encode(zlib.compress(inputfileObj.read().encode('utf-8')))
    print("The generated code is:\n\n%s\n\n" % str(inputcode))
    finalcodedata = convert(str(inputcode))
    print("The obfuscated bytes are:\n\n%s\n\n" % finalcodedata)
    outputcode = (prefix + finalcodedata) + suffix
    outputfileObj.write(outputcode)
    outputfileObj.close()
    print("File has been written to. The final code is:\n\n\n%s\n\n\n" % outputcode)

if __name__ == '__main__':
    main()
