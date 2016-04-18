import os, anydbm, hashlib, random, re, feedparser, urllib
import string, datetime, validators, json, base64, Image

import usernames, captcha

import logging
logging.basicConfig(filename='log/output.log', filemode='w', level=logging.DEBUG)

from flask import Flask, render_template, request, url_for
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from random_words import RandomWords

secret = 'this is not a secure secret'

app = Flask(__name__)

limiter = Limiter(
    app,
    key_func=get_remote_address,
    global_limits=["200 per day", "1 per second"],
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
    user = str(request.form['user'].encode('ascii', 'ignore'))
    #if not re.match(r'[a-zA-Z0-9][a-zA-Z0-9_-]+$', user):
    #    return render_template('error.html', message = 'Not a proper username!')
    db = anydbm.open(os.path.expanduser('data/usernames.db'), 'c')     # check if user is available
    #if 'user:' + user in db.keys():
    #    return render_template('error.html', message = 'This username has already been taken!')
    feedurl = request.form['feedurl']
    if not validators.url(feedurl):
        feedurl = 'http://' + feedurl
    #if not validators.url(feedurl):     # check url
    #    return render_template('error.html', message = 'This is not a valid URL!')
    hash = str(request.form['hash'])    # check if captcha is new
    db = anydbm.open(os.path.expanduser('data/used.db'), 'c')
    if hash in db.keys():
        return render_template('error.html', message = 'The captcha code you had has already expired!')
    db[hash] = 'yes'    # expiring this hash
    db.close()
    captcha = str(request.form['captcha'])    # check if captcha matches
    if not hash == hashlib.sha224(captcha + secret).hexdigest():
        return render_template('error.html', message = 'The captcha code you have typed did not match!')
    db = anydbm.open(os.path.expanduser('data/feeds.db'), 'c')    # check if user is taken
    if user in db.keys():
        return render_template('error.html', message = 'This user seems to have already been added :P')
    try:    # parsing feed
        parsedfeed = feedparser.parse(feedurl)
    except Exception as e:
        return render_template('error.html', message = 'Error parsing feed: ' + str(e))
    if not 'feed' in parsedfeed:
        return render_template('error.html', message = 'Feed does not contain basic properties!')
    if not 'title' in parsedfeed['feed']:
        feedtitle = 'No title'
    else:
        feedtitle = parsedfeed['feed']['title']
        feedtitle = (feedtitle[:100] + '...') if len(feedtitle) > 100 else feedtitle
    if not 'description' in parsedfeed['feed']:
        feeddescription = 'No description'
    else:
        feeddescription = parsedfeed['feed']['description']
        feeddescription = (feeddescription[:300] + '...') if len(feeddescription) > 300 else feeddescription
    try:
        link = parsedfeed['feed']['image']['href']
        if not validators.url(link):
            link = 'http://' + link
        if validators.url(link):
            print 1
            site = urllib.urlopen(link)
            meta = site.info()
            if int(meta.getheaders("Content-Length")[0]) < 3000000:
                print 2
                tempfile = open("/tmp/out.jpg", "wb")
                tempfile.write(site.read())
                tempfile.close()
                im = Image.open('/tmp/out.jpg')
                im.thumbnail([60, 60])
                im.save('/tmp/out2.jpg', 'JPEG')
                if os.path.getsize("/tmp/out2.jpg") < 3800000:
                    print 3
                    with open('/tmp/out2.jpg', 'rb') as image_file:
                        print 4
                        feedavatar = 'data:image/jpeg;base64,' + base64.b64encode(image_file.read())
    except:
            feedavatar = 'img/genericPerson.png'   # defaults to this if anything goes wrong
    newuser = { "name" : user,
                "url" : feedurl,
                "title" : feedtitle.encode('ascii', 'ignore'),
                "description" : feeddescription.encode('ascii', 'ignore'),
                "avatar" : feedavatar
            }
    db[user] = json.dumps(newuser)
    db.close
    return render_template('thanks.html', user = user, feedurl = feedurl)


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
    app.run(debug=True)
    app.run()

