# vim: fileencoding=utf-8 spell spelllang=en ft=python


"""
:mod:`base8x` -- Encode binary data into ASCII and vice versa
=============================================================
.. module:: base8x
    :platform: Python 2.x
    :synopsis: Base-(85 ~ 95) binary/ASCII conversion
.. moduleauthor:: Cong Ma <cma@pmo.ac.cn>

Example Usage
=============
>>> print z85codec.encode('\x86\x4f\xd2\x6f\xb5\x59\xf7\x5b')  # ZeroMQ spec
HelloWorld

Additional doctest
==================
>>> import os
>>> txt = os.urandom(1024)
>>> new = z85codec.decode(z85codec.encode(txt))
>>> print txt == new
True
>>> adobe85codec = Base8xCodec(chr(x) for x in xrange(33, 33 + 85))
>>> print adobe85codec.encode('\xff\xff\xff\xff')
s8W-!
>>> adobe85codec.decode('s8W-$')
Traceback (most recent call last):
    ...
ValueError: Tried decoding illegal sequence: (s8W-$, 0x100000002)

COPYING
=======
3-clause BSD license, see the file COPYING.
"""


import struct


_MAXVAL = 2 ** 32 - 1


def _chunkby(seq, stride, padding=None):
    """Given input iterator *seq*, yields a list for every *stride* items, and
    possibly fills the last chunk with the padding character *padding*.

    This generator yields ``(chunk, npadding)``, where ``npadding`` is the
    number of padding items at the tail.  If *padding* is :const:`None`,
    ``npadding`` gives the hypothetical number provided that padding should not
    be :const:`None`.

    >>> [(''.join(p[0]), p[1]) for p in _chunkby('abcd', 3, 'X')]
    [('abc', 0), ('dXX', 2)]

    >>> [(''.join(p[0]), p[1]) for p in _chunkby('abcde', 3)]
    [('abc', 0), ('de', 1)]
    """
    stride = int(stride)
    if stride <= 0:
        raise ValueError("Stride parameter too small")
    count = 0
    tmp = []
    for item in seq:
        tmp.append(item)
        count += 1
        if count == stride:
            yield tmp, 0
            tmp = []
            count = 0
    if count != 0:
        npadding = stride - count
        if padding is not None:
            tmp.extend([padding] * npadding)
        yield tmp, npadding


def _validate_alphabet(seq):
    """Validates the encoding alphabet *seq*.

    Returns :const:`None` if input is invalid, otherwise returns a string copy
    of the valid alphabet.

    >>> a = [chr(x) for x in xrange(35, 35 + 85)]
    >>> print _validate_alphabet(a)  # doctest: +ELLIPSIS
    #$%&...tuvw
    >>> print _validate_alphabet(a[:-1])
    None
    >>> print _validate_alphabet(a + ['\x8a'])
    None
    >>> print _validate_alphabet(['a'] + a)
    None
    """
    # Early-exit checker for the uniqueness of members.
    seen = set()
    accept = []     # Set membership is O(1), but maybe unnecessary anyway...
    # Filter out duplicate or unprintable characters.
    # Works even if seq never terminates, due to the pigeonhole principle.
    for item in seq:
        if item in seen or not 32 <= ord(item) <= 126:
            return None
        seen.add(item)
        accept.append(item)
    # Check size.  Don't use len(seq), for it doesn't have to have a length.
    if not 85 <= len(accept) <= 95:
        return None
    return "".join(accept)


def _codec_generator_factory(inchunksize, outchunksize, padchar,
                             ingroup2num, num2outgroup):
    """Factory that returns a conversion generator for codec purpose.
    By binding different parameters to the enclosed generator, the
    creations of encoding and decoding generators are unified.

    Parameters to be bound to the enclosed generator
    ------------------------------------------------
    - *inchunksize*: chunk size (in characters/bytes) of input stream
    - *outchunksize*: chunk size of output stream
    - *padchar*: padding character for incomplete chunk
    - *ingroup2num*: function taking a string built from an input chunk that
                       converts it to the internal integer value
    - *num2outgroup*: function taking an integer value that converts it to an
                        output chunk.

    The returned generator is initialized by a single argument, the input
    iterable that is to be encoded/decoded.
    """
    def codec_gen(inputseq):    # pylint:disable=C0111
        chunked = _chunkby(inputseq, inchunksize, padchar)
        for chunk, npadding in chunked:
            val = ingroup2num(b"".join(chunk))
            yield num2outgroup(val)[:(outchunksize - npadding)]
    return codec_gen


class Base8xCodec(object):
    """Base8x encoding/decoding utility class.

    An instance of the class is initialized by an ordered alphabet containing
    at least 85 unique ASCII printable characters.  For example:
    >>> Base8xCodec(chr(x) for x in xrange(40, 40 + 85))  #doctest: +ELLIPSIS
    <....Base8xCodec object at 0x...>

    The class provides two methods, :method:`encode` and :method:`decode`.

    No contraction measures (like Adobe's ``z`` encoding for 4 bytes of zeroes)
    are supported.
    """
    def __init__(self, alphabet):
        self._alphabet = _validate_alphabet(alphabet)
        if self._alphabet is None:
            raise ValueError("Invalid input alphabet")
        self._radix = len(self._alphabet)
        self._ordmap = dict(((_chr, _idx) for _idx, _chr in
                             enumerate(self._alphabet)))
        self._powersofradix = [self._radix ** _p for _p in xrange(4, -1, -1)]
        self._powersenum = [_p for _p in enumerate(self._powersofradix)]

    @staticmethod
    def _get_num_by_seq_enc(seq):
        """Get integer value by 4-byte sequence."""
        return struct.unpack(">1I", seq)[0]

    def _encode_quartet(self, num):
        """Encode a single quartet by its integer value."""
        enc = []
        for offset in self._powersofradix:
            enc.append(self._alphabet[(num // offset) % self._radix])
        return b"".join(enc)

    def _get_num_by_seq_dec(self, seq):
        """Get integer value by 5-byte sequence."""
        val = 0
        for i, offset in self._powersenum:
            char = seq[i]
            try:
                pos = self._ordmap[char]
            except KeyError:
                raise ValueError("Tried decoding sequence '%s' "
                                 "containing illegal character '%s' (0x%02x) "
                                 "at position %d" % (seq, char, ord(char), i))
            val += pos * offset
        if val > _MAXVAL:
            raise ValueError("Tried decoding illegal sequence: (%s, 0x%0x)" %
                             (seq, val))
        return val

    @staticmethod
    def _decode_quintet(num):
        """Decode a single quintet by its integer value."""
        return struct.pack(">1I", num)

    def _make_encode_gen(self):
        """Create a new encoding generator."""
        return _codec_generator_factory(4, 5, "\x00",
                                        self._get_num_by_seq_enc,
                                        self._encode_quartet)

    def _make_decode_gen(self):
        """Create a new decoding generator."""
        return _codec_generator_factory(5, 4, self._alphabet[-1],
                                        self._get_num_by_seq_dec,
                                        self._decode_quintet)

    def encode(self, text):
        """Encode text.
        *text* must be an iterable of characters or bytes.

        Returns a string.
        """
        encoder = self._make_encode_gen()
        return "".join(encoder(text))

    def decode(self, text):
        """Decode text.
        *text* must be an iterable of characters in the alphabet with valid
        5-character sequences.

        Returns a string or bytes.

        Raises :exc:`ValueError` if invalid input is encountered.
        """
        decoder = self._make_decode_gen()
        return b"".join(decoder(text))


# pylint: disable=C0103
z85codec = Base8xCodec("0123456789abcdefghijklmnopqrstuvwxyz"
                       "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                       ".-:+=^!/*?&<>()[]{}@%$#")
# pylint: enable=C0103
__all__ = ["Base8xCodec", "z85codec"]


if __name__ == "__main__":
    import doctest
    doctest.testmod()
