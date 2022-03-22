__author__ = "PierreV23 https://github.com/PierreV23"
__copyright__ = "Copyright (C) 2022 Pièrre (A.P.) V"
__license__ = "GNU General Public License v3.0"
__author__forked__ = "" # NOTE: Put your version of `__author__` in here.



import json

def load_cache():
    with open('cache.json', 'r') as file:
        return json.load(file)


def load_from_cache(series, year, round):
    key = f"({series}, {year}, {round})"
    cache = load_cache()
    if key in cache:
        return cache[key]
    else:
        return False


def save_cache(series, year, round, data):
    key = f"({series}, {year}, {round})"
    cache = load_cache()
    cache[key] = data
    with open('cache.json', 'w') as file:
        json.dump(cache, file)


def delete_from_cache(series, year, round):
    key = f"({series}, {year}, {round})"
    cache = load_cache()
    if key in cache:
        cache.pop(key)
        save_cache(series, year, round, cache)
        return True
    else:
        return False

def reset_cache():
    with open('cache.json', 'w') as file:
        json.dump({}, file)
