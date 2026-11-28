#!/usr/bin/env python3
"""Dependency-free EIP-191 personal_sign verifier.

Usage:
  eip191_verify.py <message-file> <expected-address> <signature-file>

The message and signature are read from files so neither reaches argv or a
process list. The message file is treated as exact bytes; do not add a trailing
newline unless the signer signed one.
"""

import re
import sys

P = 2**256 - 2**32 - 977
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
G = (
    0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
    0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8,
)
RC = (
    0x0000000000000001, 0x0000000000008082, 0x800000000000808A,
    0x8000000080008000, 0x000000000000808B, 0x0000000080000001,
    0x8000000080008081, 0x8000000000008009, 0x000000000000008A,
    0x0000000000000088, 0x0000000080008009, 0x000000008000000A,
    0x000000008000808B, 0x800000000000008B, 0x8000000000008089,
    0x8000000000008003, 0x8000000000008002, 0x8000000000000080,
    0x000000000000800A, 0x800000008000000A, 0x8000000080008081,
    0x8000000000008080, 0x0000000080000001, 0x8000000080008008,
)
ROT = (
    (0, 36, 3, 41, 18),
    (1, 44, 10, 45, 2),
    (62, 6, 43, 15, 61),
    (28, 55, 25, 21, 56),
    (27, 20, 39, 8, 14),
)
MASK64 = (1 << 64) - 1


def rotl64(value, shift):
    if shift == 0:
        return value
    return ((value << shift) | (value >> (64 - shift))) & MASK64


def keccak_f(lanes):
    state = [[lanes[x + 5 * y] for y in range(5)] for x in range(5)]
    for rc in RC:
        c = [state[x][0] ^ state[x][1] ^ state[x][2] ^ state[x][3] ^ state[x][4]
             for x in range(5)]
        d = [c[(x - 1) % 5] ^ rotl64(c[(x + 1) % 5], 1) for x in range(5)]
        for x in range(5):
            for y in range(5):
                state[x][y] ^= d[x]

        b = [[0] * 5 for _ in range(5)]
        for x in range(5):
            for y in range(5):
                b[y][(2 * x + 3 * y) % 5] = rotl64(state[x][y], ROT[x][y])

        for x in range(5):
            for y in range(5):
                state[x][y] = b[x][y] ^ ((~b[(x + 1) % 5][y]) & b[(x + 2) % 5][y])
        state[0][0] ^= rc
    return [state[x][y] for y in range(5) for x in range(5)]


def keccak256(data):
    rate = 136
    pad_len = rate - (len(data) % rate)
    if pad_len == 1:
        padded = data + b"\x81"
    else:
        padded = data + b"\x01" + b"\x00" * (pad_len - 2) + b"\x80"

    lanes = [0] * 25
    for offset in range(0, len(padded), rate):
        block = padded[offset:offset + rate]
        for index in range(rate // 8):
            lanes[index] ^= int.from_bytes(block[index * 8:index * 8 + 8], "little")
        lanes = keccak_f(lanes)
    return b"".join(lane.to_bytes(8, "little") for lane in lanes)[:32]


def inv(value, modulus):
    return pow(value, modulus - 2, modulus)


def point_add(a, b):
    if a is None:
        return b
    if b is None:
        return a
    x1, y1 = a
    x2, y2 = b
    if x1 == x2 and (y1 + y2) % P == 0:
        return None
    if a == b:
        lam = (3 * x1 * x1 * inv(2 * y1, P)) % P
    else:
        lam = ((y2 - y1) * inv(x2 - x1, P)) % P
    x3 = (lam * lam - x1 - x2) % P
    y3 = (lam * (x1 - x3) - y1) % P
    return (x3, y3)


def point_mul(scalar, point):
    result = None
    addend = point
    while scalar:
        if scalar & 1:
            result = point_add(result, addend)
        addend = point_add(addend, addend)
        scalar >>= 1
    return result


def personal_message_hash(message):
    prefix = b"\x19Ethereum Signed Message:\n" + str(len(message)).encode("ascii")
    return keccak256(prefix + message)


def recover_address(message, signature):
    text = signature.decode("ascii", "strict").strip()
    if not re.fullmatch(r"0x[0-9a-fA-F]{130}", text):
        raise ValueError("signature is not a 65-byte EIP-191 signature")
    raw = bytes.fromhex(text[2:])
    r = int.from_bytes(raw[:32], "big")
    s = int.from_bytes(raw[32:64], "big")
    v = raw[64]
    if v in (0, 1):
        recid = v
    elif v in (27, 28):
        recid = v - 27
    else:
        raise ValueError("signature recovery id is not 0/1 or 27/28")
    if not (1 <= r < N and 1 <= s < N):
        raise ValueError("signature scalar is out of range")
    if s > N // 2:
        raise ValueError("signature uses a non-canonical high-s value")

    alpha = (pow(r, 3, P) + 7) % P
    beta = pow(alpha, (P + 1) // 4, P)
    if (beta * beta) % P != alpha:
        raise ValueError("signature r is not on secp256k1")
    y = beta if (beta & 1) == recid else P - beta
    point_r = (r, y)
    if point_mul(N, point_r) is not None:
        raise ValueError("signature r is not a valid curve point")

    digest = int.from_bytes(personal_message_hash(message), "big")
    r_inv = inv(r, N)
    u1 = (-digest * r_inv) % N
    u2 = (s * r_inv) % N
    public = point_add(point_mul(u1, G), point_mul(u2, point_r))
    if public is None:
        raise ValueError("signature recovery failed")
    encoded = public[0].to_bytes(32, "big") + public[1].to_bytes(32, "big")
    return "0x" + keccak256(encoded)[-20:].hex()


def main(argv):
    if len(argv) != 4:
        print("usage: eip191_verify.py <message-file> <expected-address> <signature-file>",
              file=sys.stderr)
        return 2
    try:
        with open(argv[1], "rb") as handle:
            message = handle.read()
        with open(argv[3], "rb") as handle:
            signature = handle.read()
        expected = argv[2].strip().lower()
        if not re.fullmatch(r"0x[0-9a-f]{40}", expected):
            raise ValueError("expected address is not an EVM address")
        recovered = recover_address(message, signature)
        if recovered != expected:
            raise ValueError("signature does not verify against the expected address")
    except (OSError, UnicodeError, ValueError) as error:
        print("verification failed: " + str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
