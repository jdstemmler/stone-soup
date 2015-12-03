import io
import json

def read_settings(f):
    with io.open(f) as cred:
        settings = json.load(cred)
    return settings

def load_setting(f, item=None):
    settings = read_settings(f)
    if item is None:
        return settings
    else:
        return settings[item]
