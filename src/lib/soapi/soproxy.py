#!/usr/bin/env python
# coding: utf-8

from lib.utils import import_object

def make_api_call(provider, api_name, *args, **kw):
    module = import_object('lib.soapi.{0}'.format(provider))
    func = getattr(module, api_name)
    return func(*args, **kw) if func else None

