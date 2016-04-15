import os
import anydbm
import captcha


import logging
logging.basicConfig(filename='log/output.log', filemode='w', level=logging.DEBUG)

from flask import Flask, jsonify, render_template
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

#from bitcoinrpc.authproxy import AuthServiceProxy

app = Flask(__name__)

limiter = Limiter(
    app,
    key_func=get_remote_address,
    global_limits=["20 per day", "1 per second"],
)

@app.route('/')
@limiter.limit("20 per day")
def index():
    word = captcha.new_word()
    captcha.gen_captcha(word[0], 'static/porkys.ttf', 25, 'static/captchas/' + word[1] + '.jpg', fmt='JPEG')
    return word[0] + '<img src="static/captchas/' + word[1] + '.jpg" alt="Captcha" style="height:80px;">'

@app.route('/view')
@limiter.limit("200 per day")
def view():
    db = anydbm.open(os.path.expanduser('data/feeds.db'), 'c')
    outputlist = []
    for key, value in db.iteritems():
        temp = [key, value]
        outputlist.append(temp)
    db.close()
    return render_template('view.html', feeds=outputlist)

@app.route('/data')
def names():
    data = {"names": ["John", "Jacob", "Julie", "Jennifer"]}
    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True)
    # app.run()

