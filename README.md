# mini-binary-coded-decimal

Encodes and decodes non-negative integers to and from packed and unpacked BCD (Binary-Coded Decimal) representations.

```python
from mini_binary_coded_decimal import (
    encode_packed,
    decode_packed,
    encode_unpacked,
    decode_unpacked,
)

encode_packed(42)        # b'\x42'
decode_packed(b'\x01\x23')  # 123
encode_unpacked(42)      # b'\x04\x02'
decode_unpacked(b'\x04\x02')  # 42
```

## Why

BCD still shows up in legacy financial systems, embedded displays, and
fixed-length wire formats where decimal digit alignment matters more than
compactness. This library gives you a tiny, dependency-free way to move
between ints and the two common BCD layouts without pulling in anything
else.

## What it does and doesn't do

Only non-negative integers are supported. Real BCD sign conventions vary
wildly across platforms (zoned signs, packed-sign nibbles like 0xC/0xD,
etc.), so rather than guess one and get it wrong for half of you, the sign
is left out entirely. If you need negatives, carry the sign yourself and
encode the absolute value.

## The awkward edge

Packed BCD stores two digits per byte, so an odd digit count is padded with
a leading zero nibble. On decode, any nibble outside 0x0-0x9 raises — this
includes the 0xF, 0xC, and 0xD values that other formats use as sign
markers. If your data carries a sign nibble, strip it before handing the
bytes to `decode_packed`.

Unpacked BCD here means one digit per byte with the high nibble always zero
(the layout of an EBCDIC zoned field with zone bits stripped, not ASCII
digit codes). `decode_unpacked` requires the high nibble to be zero.

## API

- `encode_packed(n, digits=0) -> bytes`
- `decode_packed(data: bytes) -> int`
- `encode_unpacked(n, digits=0) -> bytes`
- `decode_unpacked(data: bytes) -> int`
