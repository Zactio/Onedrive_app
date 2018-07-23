from flask import Flask, render_template
app = Flask(__name__, template_folder='static/templates')
app.debug = True

@app.route('/', methods=['GET'])
def upload():
    return render_template('index.html')

@app.route('/my-link/')
def my_link():
	print ('I got clicked!')

	return 'Click.'

if __name__ == '__main__':
  app.run(debug=True)

