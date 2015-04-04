#!/usr/bin/python
"""Generate random secret keys for WordPress's wp-config.php file."""
# See also:  https://api.wordpress.org/secret-key/1.1/salt/


import os
import base8x


w92codec = base8x.Base8xCodec("0123456789abcdefghijklmnopqrstuvwxyz"
                              "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                              "`,~| _;.-:+=^!/*?&<>()[]{}@%$#")
WPVARS = ("AUTH_KEY",
          "SECURE_AUTH_KEY",
          "LOGGED_IN_KEY",
          "NONCE_KEY",
          "AUTH_SALT",
          "SECURE_AUTH_SALT",
          "LOGGED_IN_SALT",
          "NONCE_SALT")
JSIZE = max([len(_var) for _var in WPVARS]) + 4  # 2 * quotes + comma + space


def genkeyfrom(size):
    """Returns text representation of random key of given size in bytes."""
    return w92codec.encode(os.urandom(size))


def pronouncewpline(wpvar, secret):
    """Returns a PHP statement line for the given WP variable wpvar
    and secret random key secret.
    """
    v_tmp = "'%s'," % wpvar
    v_jst = v_tmp.ljust(JSIZE)
    return "define(%s'%s');" % (v_jst, secret)


def use(nbits):
    """Dumps the generated PHP statements to stdout.
    Generates at least nbits bits of randomness for each WordPress key.
    """
    nbytes, rem = divmod(nbits, 8)
    nbytes += int(rem > 0)
    for var in WPVARS:
        secretkey = genkeyfrom(nbytes)
        print pronouncewpline(var, secretkey)
    return None


if __name__ == "__main__":
    import sys
    try:
        bits = int(sys.argv[1])
    except IndexError:
        bits = 320
    use(bits)
