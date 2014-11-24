#!/usr/bin/env python
# coding: utf-8

from hashlib import sha1
from random import choice
from string import digits, ascii_lowercase


def rand_salt(len):
    return ''.join(choice(ascii_lowercase + digits) for _ in range(len))


def password_hash(raw_password, salt):
    return sha1(raw_password + ':' + salt).hexdigest()[:32]


def import_object(name):
    """Imports an object by name.

    import_object('x') is equivalent to 'import x'.
    import_object('x.y.z') is equivalent to 'from x.y import z'.

    """
    if name.count('.') == 0:
        return __import__(name, None, None)

    parts = name.split('.')
    obj = __import__('.'.join(parts[:-1]), None, None, [parts[-1]], 0)
    try:
        return getattr(obj, parts[-1])
    except AttributeError:
        raise ImportError("No module named %s" % parts[-1])

def random_name():
    return rand_salt(16)

