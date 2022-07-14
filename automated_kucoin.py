from flask import Flask, render_template, request
application = Flask(__name__)
app = application
import my_kucoin

api_key = "62c7f299686bb40001c17f11"
secret_key = "87ecfc58-8a0b-4693-a007-5ff3d25fd10a"
passphrase = "greentrees1111"

@app.route('/', methods=['GET', 'POST'])
# @app.route('/<int:uid>', methods=['GET','POST'])
def index():
    if request.method == 'POST':
        # name = request.form['name']
        # context = request.form['context']
        myKucoin = my_kucoin.Mykucoin(api_key, secret_key, passphrase)
        print('coin: {0}'.format(myKucoin.printit()[0]))
        print('buy: {0}'.format(myKucoin.printit()[1]))
        return render_template('home.html', json_result=myKucoin.printit()[0], len=len(myKucoin.printit()))
        # return render_template('home.html', json_result=myKucoin.printit(), len=len(myKucoin.printit()))
    else:
        myKucoin = my_kucoin.Mykucoin(api_key, secret_key, passphrase)
        return render_template('home.html', json_result=myKucoin.printit(), len=len(myKucoin.printit()))

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    myKucoin = my_kucoin.Mykucoin(api_key, secret_key, passphrase)
    return render_template('index.html', json_result=myKucoin.printit())


if __name__ == "__main__":
    # application.debug = True
    application.run(threaded=True)
