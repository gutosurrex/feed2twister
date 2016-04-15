import os
import anydbm
import captcha
import hashlib
import random
import string

import logging
logging.basicConfig(filename='log/output.log', filemode='w', level=logging.DEBUG)


from flask import Flask, jsonify, render_template, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from random_words import RandomWords

#from bitcoinrpc.authproxy import AuthServiceProxy

app = Flask(__name__)

limiter = Limiter(
    app,
    key_func=get_remote_address,
    global_limits=["20 per day", "1 per second"],
)

secret = 'fj28sdkfj1lwkdjf8s8dufh1kkkk'

def id_generator(size=6, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

@app.route('/')
@limiter.limit("20 per day")
def index():
    #word = new_word()
    word = id_generator()
    hash = hashlib.sha224(word + secret).hexdigest()
    filename = 'static/captchas/' + hash + '.jpg'
    captcha.gen_captcha(word, 'static/porkys.ttf', 25, filename, fmt='JPEG')
    return render_template('form.html', filename = filename)

@app.route('/submitted/', methods=['POST'])
def submitted():
    user = request.form['user']
    feedurl = request.form['feedurl']
    captcha = request.form['captcha']
    hash = hashlib.sha224(captcha + secret).hexdigest()
    filename = 'static/captchas/' + hash + '.jpg'
    if os.path.isfile(filename):
        return render_template('thanks.html', user = user, feedurl = feedurl)
    return 'error'

@app.route('/view')
@limiter.limit("200 per day")
def view():
    db = anydbm.open(os.path.expanduser('data/feeds.db'), 'c')
    outputlist = []
    for key, value in db.iteritems():
        temp = [key, value]
        outputlist.append(temp)
    db.close()
    return render_template('view.html', feeds = outputlist)

@app.route('/data')
def names():
    data = {"names": ["John", "Jacob", "Julie", "Jennifer"]}
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
    app.run()

