from flask import Flask, render_template, request, session, redirect
import uuid

app = Flask(__name__)
app.secret_key = "asdf1234" #TODO:CHANGE THIS TO SOMETHING MORE SECURE

@app.route('/favicon.ico')
def favicon():
    return redirect('/static/favicon.ico')

@app.errorhandler(404)
def page_not_found(e):
    print(request.url)
    
#Handle form request
@app.route('/submit-form/', methods=['POST'])
def handle_form():
    print("#"*80)
    print("user_id: %s" % session['user_id'])
    print('user_id' in session)
    if 'user_id' in session:
        print("Submitted form with name: %s" % request.form['name'])
        session['name'] = request.form['name']
    return redirect('/')

@app.route('/', methods=['GET'])
def index():
    if 'user_id' not in session:
        session['user_id'] = uuid.uuid4()
        session['name'] = None
        return render_template('index.html')
    else:
        print("user_id: %s" % session['user_id'])
        return render_template('index.html', message="Welcome %s" % session['name'])

if __name__ == '__main__':
    app.run(debug=True)