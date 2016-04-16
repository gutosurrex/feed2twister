import os, anydbm, captcha, hashlib, random, re
import string, datetime, usernames, validators

import logging
logging.basicConfig(filename='log/output.log', filemode='w', level=logging.DEBUG)

from flask import Flask, jsonify, render_template, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from random_words import RandomWords

secret = 'fj28sdkfj1lwkdjf8s8dufh1kkkk'

app = Flask(__name__)

limiter = Limiter(
    app,
    key_func=get_remote_address,
    global_limits=["20 per day", "1 per second"],
)

def id_generator(size=6, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def clean():
    dir_to_search = os.path.curdir
    for dirpath, dirnames, filenames in os.walk('static/captchas/'):
        for file in filenames:
            curpath = os.path.join(dirpath, file)
            file_modified = datetime.datetime.fromtimestamp(os.path.getmtime(curpath))
            if datetime.datetime.now() - file_modified > datetime.timedelta(hours=1):
                os.remove(curpath)

@app.route('/')
@limiter.limit("20 per day")
def index():
    clean()
    word = id_generator()
    hash = hashlib.sha224(word + secret).hexdigest()
    filename = 'static/captchas/' + hash + '.jpg'
    captcha.gen_captcha(word, 'static/porkys.ttf', 25, filename, fmt='JPEG')
    return render_template('form.html', filename = filename, hash = hash)

@app.route('/submitted/', methods=['POST'])
@limiter.limit("20 per day")
def submitted():
    user = request.form['user']
    if not re.match(r'[a-zA-Z0-9][a-zA-Z0-9_-]+$', user):
        return render_template('error.html', message = 'Not a proper username!')
    db = anydbm.open(os.path.expanduser('data/usernames.db'), 'c')
    if 'user:' + user in db.keys():
        return render_template('error.html', message = 'This username has already been taken!')
    hash = str(request.form['hash'])
    feedurl = request.form['feedurl']
    if not validators.url(feedurl):
        return render_template('error.html', message = 'This is not a valid URL!')
    captcha = request.form['captcha']
    filename = 'static/captchas/' + hash + '.jpg'
    db = anydbm.open(os.path.expanduser('data/used.db'), 'c')
    if hash in db.keys():
        return render_template('error.html', message = 'The captcha code you had has already expired!')
    db[hash] = 'yes'
    db.close()
    if hash == hashlib.sha224(captcha + secret).hexdigest():
        return render_template('thanks.html', user = user, feedurl = feedurl)
    return render_template('error.html', message = 'The captcha code you have typed did not match!')

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

if __name__ == '__main__':
    # app.run(debug=True)
    app.run()

