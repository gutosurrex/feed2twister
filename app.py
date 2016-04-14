import captcha

from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    word = captcha.new_word()
    captcha.gen_captcha(word[0], 'static/porkys.ttf', 25, 'static/' + word[1] + '.jpg', fmt='JPEG')
    return word[0] + '<img src="static/' + word[1] + '.jpg" alt="Captcha" style="width:200px;height:30px;">'

@app.route('/data')
def names():
    data = {"names": ["John", "Jacob", "Julie", "Jennifer"]}
    return jsonify(data)


if __name__ == '__main__':
    app.run()


