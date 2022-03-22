__author__ = "PierreV23 https://github.com/PierreV23"
__copyright__ = "Copyright (C) 2022 Pièrre (A.P.) V"
__license__ = "GNU General Public License v3.0"
__author__forked__ = "" # NOTE: Put your version of `__author__` in here.

import json


def get_json(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
        return data

def set_json(filename, data, indent = None):
    with open(filename, 'w') as file:
        if indent:
            json.dump(data, file, indent = indent)
        else:
            json.dump(data, file)