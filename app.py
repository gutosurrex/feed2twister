import captcha

from flask import Flask, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

limiter = Limiter(
    app,
    key_func=get_remote_address,
    global_limits=["2 per minute", "1 per second"],
)

@app.route('/')
@limiter.limit("2 per minute")
def index():
    word = captcha.new_word()
    captcha.gen_captcha(word[0], 'static/porkys.ttf', 25, 'static/captchas/' + word[1] + '.jpg', fmt='JPEG')
    return word[0] + '<img src="static/captchas/' + word[1] + '.jpg" alt="Captcha" style="height:80px;">'

@app.route('/data')
def names():
    data = {"names": ["John", "Jacob", "Julie", "Jennifer"]}
    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True)
    # app.run()

