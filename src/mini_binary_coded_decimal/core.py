"""Binary-Coded Decimal encode and decode for non-negative integers.

Design decisions
----------------

* **Non-negative integers only.** BCD historically represents the decimal
  digits of a number; the sign is normally carried in a separate nibble whose
  format varies wildly across platforms (zoned, packed-sign, etc). Rather
  than guess a sign convention, we only handle numbers >= 0. Callers
  wanting negative values should carry the sign out-of-band.

* **Padding.** A packed BCD string must have an even number of hex digits
  (two digits per byte). When the requested number of digits is odd we pad
  the most-significant side with a zero nibble so the hex representation is
  always even-length, matching the common packed-BCD wire format.

* **Strict decode.** `decode_*` rejects nibbles outside 0x0-0x9 so that a
  stray 0xF (a common sign nibble in real systems) raises rather than
  silently producing garbage. Padding zeros in the high nibble are allowed.

* **Unpacked BCD = one digit per byte**, high nibble zero. This is the
  ASCII-digit layout stored in EBCDIC zoned fields (minus the zone bits).
"""


_MAX_NIBBLE = 0x9


def encode_packed(n: int, digits: int = 0) -> bytes:
    """Encode a non-negative integer as packed BCD.

    Packed BCD stores two decimal digits per byte. The high nibble of the
    leftmost byte is zero-padded when the number of digits is odd.

    Args:
        n: Non-negative integer to encode.
        digits: Minimum number of decimal digits to allocate. 0 means
            "just enough for the value" (at least 1, so 0 encodes to a single
            zero digit, which then pads to two digits / one byte).

    Returns:
        Packed-BCD bytes, always with an even number of nibbles.

    Raises:
        ValueError: if n is negative or digits is negative.
        ValueError: if n has more digits than `digits` allows.
    """
    if not isinstance(n, int):
        raise TypeError("n must be an int")
    if not isinstance(digits, int):
        raise TypeError("digits must be an int")
    if n < 0:
        raise ValueError("n must be non-negative")
    if digits < 0:
        raise ValueError("digits must be non-negative")

    text = str(n)
    if digits > 0 and len(text) > digits:
        raise ValueError("n has more digits than digits allows")
    if len(text) < digits:
        text = text.zfill(digits)

    # Odd digit counts get a leading 0 so the packed result is whole bytes.
    if len(text) % 2 == 1:
        text = "0" + text

    out = bytearray()
    for i in range(0, len(text), 2):
        hi = ord(text[i]) - ord("0")
        lo = ord(text[i + 1]) - ord("0")
        out.append((hi << 4) | lo)
    return bytes(out)


def decode_packed(data: bytes) -> int:
    """Decode packed BCD to an int.

    Each byte is split into two nibbles; each must be 0x0-0x9. A leading
    zero nibble (padding) is fine. Other non-decimal nibbles raise.

    Args:
        data: Packed-BCD bytes.

    Returns:
        The decoded non-negative integer.

    Raises:
        ValueError: if any nibble is not 0x0-0x9.
    """
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError("data must be bytes")
    digits = []
    for b in data:
        hi = (b >> 4) & 0xF
        lo = b & 0xF
        for nib in (hi, lo):
            if nib > _MAX_NIBBLE:
                raise ValueError(f"invalid BCD nibble: 0x{nib:X}")
            digits.append(nib)
    return int("".join(str(d) for d in digits))


def encode_unpacked(n: int, digits: int = 0) -> bytes:
    """Encode a non-negative integer as unpacked BCD (one digit per byte).

    Each output byte has its high nibble set to 0 and its low nibble holding
    one decimal digit. This is the layout of an EBCDIC zoned field with the
    zone bits stripped (ASCII digit values are not used).

    Args:
        n: Non-negative integer to encode.
        digits: Minimum number of output bytes. 0 = exactly the digit count.

    Returns:
        Unpacked-BCD bytes, one decimal digit per byte.

    Raises:
        ValueError: if n is negative or digits is negative.
    """
    if not isinstance(n, int):
        raise TypeError("n must be an int")
    if not isinstance(digits, int):
        raise TypeError("digits must be an int")
    if n < 0:
        raise ValueError("n must be non-negative")
    if digits < 0:
        raise ValueError("digits must be non-negative")

    text = str(n)
    if digits > 0 and len(text) > digits:
        raise ValueError("n has more digits than digits allows")
    if len(text) < digits:
        text = text.zfill(digits)
    return bytes((ord(c) - ord("0")) & 0xF for c in text)


def decode_unpacked(data: bytes) -> int:
    """Decode unpacked BCD to an int.

    Each byte's low nibble is treated as one decimal digit; the high nibble
    is required to be zero (the unpacked encoding we produce never sets it,
    so we require it on decode for symmetry).

    Args:
        data: Unpacked-BCD bytes.

    Returns:
        The decoded non-negative integer.

    Raises:
        ValueError: if any byte's high nibble is non-zero, or if the low
            nibble is not 0x0-0x9.
    """
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError("data must be bytes")
    digits = []
    for b in data:
        if b & 0xF0:
            raise ValueError("non-zero high nibble in unpacked BCD")
        lo = b & 0xF
        if lo > _MAX_NIBBLE:
            raise ValueError(f"invalid BCD nibble: 0x{lo:X}")
        digits.append(lo)
    return int("".join(str(d) for d in digits))
