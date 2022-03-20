#!/usr/bin/env python3

class NoneClass(object):
    """
    Helper class to represent None
    """
    def __init__(self, message):
        self.message = message

    def __getattr__(self, attr):
        print(self.message)
