from configparser import ConfigParser
import os

parser = ConfigParser()
cwd = os.getcwd()
config_path = cwd + r'/configuration/config.ini'
parser.read(config_path)


def get_db_config():
    db = {}
    if parser.has_section('couchbase'):
        params = parser.items('couchbase')
        for param in params:
            db[param[0]] = param[1]
    return db

def get_secret():
    db = {}
    if parser.has_section('api'):
        params = parser.items('api')
        secret = next((p for p in params if p[0] == 'secret'), None)
        return secret[1] if secret else None

    return None

def get_ttl():
    db = {}
    if parser.has_section('couchbase'):
        params = parser.items('couchbase')
        ttl = next((p for p in params if p[0] == 'ttl'), None)
        return ttl[1] if ttl else None

    return None