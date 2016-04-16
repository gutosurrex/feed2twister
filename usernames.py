#!/usr/bin/python
#
# This sample script is a username crawler: it will obtain all known usernames
# from block chain.
#
# Downloaded data is cached in a database file, so it may be executed
# again and it won't need to get everything all over again (you may run it
# from cron scripts, for example)

import sys, anydbm, time, os, ConfigParser

from xdg.BaseDirectory import xdg_config_home
main_config_file = ConfigParser.ConfigParser()
main_config_file.read([os.path.expanduser('feed2twister.conf'), os.path.join(xdg_config_home, 'feed2twister.conf'), os.path.expanduser('~/.feed2twister.conf')])
main_config = main_config_file.defaults()

def get_bool_conf_option(option):
    if option in main_config and main_config[option]:
        v = main_config[option]
        return str(v).lower() in ('yes', 'true', 't', '1')
    return False

def get_array_conf_option(option):
    if option in main_config and main_config[option]:
        return main_config[option].split("\n")
    return []

dbfilename = 'data/usernames.db'
cacheTimeout = 24*3600

try:
    from bitcoinrpc.authproxy import AuthServiceProxy
except ImportError as exc:
    sys.stderr.write("Error: install python-bitcoinrpc (https://github.com/jgarzik/python-bitcoinrpc)\n")
    exit(-1)

twister = AuthServiceProxy(main_config['rpc_url'])

try:
    db = anydbm.open(os.path.expanduser(dbfilename), 'c')
    if not 'lastblockhash' in db.keys():
        db['lastblockhash'] = twister.getblockhash(0)
    nextHash = db['lastblockhash']
except ImportError as exc:
    sys.stderr.write("Did not manage to open databases\n")
    exit(-1)

while True:
    block = twister.getblock(nextHash)
    db['lastblockhash'] = block["hash"]
    #print str(block["height"]) + "\r",
    usernames = block["usernames"]
    for u in usernames:
        if not str(u) in db.keys():
            db['user:' + str(u)] = 'taken'
    if block.has_key("nextblockhash"):
        nextHash = block["nextblockhash"]
    else:
        break

db.close()

