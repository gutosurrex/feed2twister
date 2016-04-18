import os, anydbm
import sys

from bitcoinrpc.authproxy import AuthServiceProxy

import logging
logging.basicConfig(filename='log/createuser.log', filemode='w', level=logging.DEBUG)

db = anydbm.open(os.path.expanduser('data/feeds.db'), 'c')    # check if user is taken

for key, value in db.iteritems():
    print key, value

    secretkey = twister.createwalletuser('username')
    twister.sendnewusertransaction('username')

'I tryed with user sopenadi...'
    
