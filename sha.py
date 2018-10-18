from math import log
from operator import xor
from copy import deepcopy
from functools import reduce
RoundConstants = [
    0x0000000000000001, 0x0000000000008082, 0x800000000000808A, 0x8000000080008000,
    0x000000000000808B, 0x0000000080000001, 0x8000000080008081, 0x8000000000008009,
    0x000000000000008A, 0x0000000000000088, 0x0000000080008009, 0x000000008000000A,
    0x000000008000808B, 0x800000000000008B, 0x8000000000008089, 0x8000000000008003,
    0x8000000000008002, 0x8000000000000080, 0x000000000000800A, 0x800000008000000A,
    0x8000000080008081, 0x8000000000008080, 0x0000000080000001, 0x8000000080008008
]
RotationConstants = [
    [0,  1,  62, 28, 27],
    [36, 44, 6,  55, 20],
    [3,  10, 43, 25, 39],
    [41, 45, 15, 21, 8],
    [18, 2,  61, 56, 14]
]
Masks = [(1 << i) - 1 for i in range(65)]
def bits2bytes(x):
    return (int(x) + 7) // 8
def rol(value, left, bits):
    top = value >> (bits - left)
    bot = (value & Masks[bits - left]) << left
    return bot | top
def ror(value, right, bits):
    top = value >> right
    bot = (value & Masks[right]) << (bits - right)
    return bot | top
def multirate_padding(used_bytes, align_bytes):
    padlen = align_bytes - used_bytes
    if padlen == 0:
        padlen = align_bytes
    # note: padding done in 'internal bit ordering', wherein LSB is leftmost
    if padlen == 1:
        return [0x81]
    else:
        return [0x01] + ([0x00] * (padlen - 2)) + [0x80]
def sha_padding(used_bytes, align_bytes):
    padlen = align_bytes - (used_bytes % align_bytes)
    if padlen == 1:
        return [0x86]
    elif padlen == 2:
        return [0x06, 0x80]
    else:
        return [0x06] + ([0x00] * (padlen - 2)) + [0x80]
def keccak_f(state):
    def keccak_round(a, rc):
        w, h = state.W, state.H
        rangew, rangeh = state.rangeW, state.rangeH
        lanew = state.lanew
        zero = state.zero
        c = [reduce(xor, a[x]) for x in rangew]
        d = [0] * w
        for x in rangew:
            d[x] = c[(x - 1) % w] ^ rol(c[(x + 1) % w], 1, lanew)
            for y in rangeh:
                a[x][y] ^= d[x]
        b = zero()
        for x in rangew:
            for y in rangeh:
                b[y % w][(2 * x + 3 * y) % h] = rol(a[x][y], RotationConstants[y][x], lanew)
        for x in rangew:
            for y in rangeh:
                a[x][y] = b[x][y] ^ ((~ b[(x + 1) % w][y]) & b[(x + 2) % w][y])
        # iota
        a[0][0] ^= rc
    nr = 12 + 2 * int(log(state.lanew, 2))
    for ir in range(nr):
        keccak_round(state.s, RoundConstants[ir])
class KeccakState:
    W = 5
    H = 5
    rangeW = range(W)
    rangeH = range(H)
    @staticmethod
    def zero():
        return [[0] * KeccakState.W for _ in KeccakState.rangeH]
    @staticmethod
    def format(st):
        rows = []

        def fmt(stx):
            return '%016x' % stx

        for y in KeccakState.rangeH:
            row = []
            for x in KeccakState.rangeW:
                row.append(fmt(st[x][y]))
            rows.append(' '.join(row))
        return '\n'.join(rows)

    @staticmethod
    def lane2bytes(s, w):
        """
        Converts the lane s to a sequence of byte values,
        assuming a lane is w bits.
        """
        o = []
        for b in range(0, w, 8):
            o.append((s >> b) & 0xff)
        return o

    @staticmethod
    def bytes2lane(bb):
        """
        Converts a sequence of byte values to a lane.
        """
        r = 0
        for b in reversed(bb):
            r = r << 8 | b
        return r

    @staticmethod
    def bytes2str(bb):
        """
        Converts a sequence of byte values to a string.
        """
        return bytes(bb)

    @staticmethod
    def str2bytes(ss):
        """
        Converts a string to a sequence of byte values.
        """
        return map(ord, ss)

    def __init__(self, bitrate, b):
        self.bitrate = bitrate
        self.b = b

        # only byte-aligned
        assert self.bitrate % 8 == 0
        self.bitrate_bytes = bits2bytes(self.bitrate)

        assert self.b % 25 == 0
        self.lanew = self.b // 25

        self.s = KeccakState.zero()

    def __str__(self):
        return KeccakState.format(self.s)

    def absorb(self, bb):
        """
        Mixes in the given bitrate-length string to the state.
        """
        assert len(bb) == self.bitrate_bytes

        bb += [0] * bits2bytes(self.b - self.bitrate)
        i = 0

        for y in self.rangeH:
            for x in self.rangeW:
                self.s[x][y] ^= KeccakState.bytes2lane(bb[i:i + 8])
                i += 8

    def squeeze(self):
        """
        Returns the bitrate-length prefix of the state to be output.
        """
        return self.get_bytes()[:self.bitrate_bytes]

    def get_bytes(self):
        """
        Convert whole state to a byte string.
        """
        out = [0] * bits2bytes(self.b)
        i = 0
        for y in self.rangeH:
            for x in self.rangeW:
                v = KeccakState.lane2bytes(self.s[x][y], self.lanew)
                out[i:i + 8] = v
                i += 8
        return out

    def set_bytes(self, bb):
        """
        Set whole state from byte string, which is assumed
        to be the correct length.
        """
        i = 0
        for y in self.rangeH:
            for x in self.rangeW:
                self.s[x][y] = KeccakState.bytes2lane(bb[i:i + 8])
                i += 8


class KeccakSponge:
    def __init__(self, bitrate, width, padfn, permfn):
        self.state = KeccakState(bitrate, width)
        self.padfn = padfn
        self.permfn = permfn
        self.buffer = []

    def copy(self):
        return deepcopy(self)

    def absorb_block(self, bb):
        assert len(bb) == self.state.bitrate_bytes
        self.state.absorb(bb)
        self.permfn(self.state)

    def absorb(self, s):
        self.buffer += s

        while len(self.buffer) >= self.state.bitrate_bytes:
            self.absorb_block(self.buffer[:self.state.bitrate_bytes])
            self.buffer = self.buffer[self.state.bitrate_bytes:]

    def absorb_final(self):
        padded = self.buffer + self.padfn(len(self.buffer), self.state.bitrate_bytes)
        self.absorb_block(padded)
        self.buffer = []

    def squeeze_once(self):
        rc = self.state.squeeze()
        self.permfn(self.state)
        return rc

    def squeeze(self, l):
        z = self.squeeze_once()
        while len(z) < l:
            z += self.squeeze_once()
        return z[:l]


class KeccakHash:
    """
    The Keccak hash function, with a hashlib-compatible interface.
    """

    def __init__(self, bitrate_bits, capacity_bits, output_bits):
        # our in-absorption sponge. this is never given padding
        assert bitrate_bits + capacity_bits in (25, 50, 100, 200, 400, 800, 1600)
        self.sponge = KeccakSponge(bitrate_bits, bitrate_bits + capacity_bits,
                                   multirate_padding,
                                   keccak_f)

        # hashlib interface members
        assert output_bits % 8 == 0
        self.digest_size = bits2bytes(output_bits)
        self.block_size = bits2bytes(bitrate_bits)

    def __repr__(self):
        inf = (self.sponge.state.bitrate,
               self.sponge.state.b - self.sponge.state.bitrate,
               self.digest_size * 8)
        return '<KeccakHash with r=%d, c=%d, image=%d>' % inf

    def copy(self):
        return deepcopy(self)

    def update(self, s):
        self.sponge.absorb(s)

    def digest(self):
        finalised = self.sponge.copy()
        finalised.absorb_final()
        digest = finalised.squeeze(self.digest_size)
        return KeccakState.bytes2str(digest)

    def hexdigest(self):
        return self.digest().hex()

    @staticmethod
    def preset(bitrate_bits, capacity_bits, output_bits):
        """
        Returns a factory function for the given bitrate, sponge capacity and output length.
        The function accepts an optional initial input, ala hashlib.
        """

        def create(initial_input=None):
            h = KeccakHash(bitrate_bits, capacity_bits, output_bits)
            if initial_input is not None:
                h.update(initial_input)
            return h

        return create


class SHA3Hash:
    """
    The Keccak hash function, with a hashlib-compatible interface.
    """

    def __init__(self, bitrate_bits, capacity_bits, output_bits):
        # our in-absorption sponge. this is never given padding
        assert bitrate_bits + capacity_bits in (25, 50, 100, 200, 400, 800, 1600)
        self.sponge = KeccakSponge(bitrate_bits, bitrate_bits + capacity_bits,
                                   sha_padding,
                                   keccak_f)

        # hashlib interface members
        assert output_bits % 8 == 0
        self.digest_size = bits2bytes(output_bits)
        self.block_size = bits2bytes(bitrate_bits)

    def __repr__(self):
        inf = (self.sponge.state.bitrate,
               self.sponge.state.b - self.sponge.state.bitrate,
               self.digest_size * 8)
        return '<SHA3Hash with r=%d, c=%d, image=%d>' % inf

    def copy(self):
        return deepcopy(self)

    def update(self, s):
        self.sponge.absorb(s)

    def digest(self):
        finalised = self.sponge.copy()
        finalised.absorb_final()
        digest = finalised.squeeze(self.digest_size)
        return KeccakState.bytes2str(digest)

    def hexdigest(self):
        return self.digest().hex()

    @staticmethod
    def preset(bitrate_bits, capacity_bits, output_bits):
        """
        Returns a factory function for the given bitrate, sponge capacity and output length.
        The function accepts an optional initial input, ala hashlib.
        """

        def create(initial_input=None):
            h = SHA3Hash(bitrate_bits, capacity_bits, output_bits)
            if initial_input is not None:
                h.update(initial_input)
            return h

        return create


# Keccak parameter presets
Keccak224 = KeccakHash.preset(1152, 448, 224)
Keccak256 = KeccakHash.preset(1088, 512, 256)
Keccak384 = KeccakHash.preset(832, 768, 384)
Keccak512 = KeccakHash.preset(576, 1024, 512)

# SHA3 parameter presets
SHA3_224 = SHA3Hash.preset(1152, 448, 224)
SHA3_256 = SHA3Hash.preset(1086, 512, 256)
SHA3_384 = SHA3Hash.preset(832, 768, 384)
SHA3_512 = SHA3Hash.preset(576, 1024, 512)
