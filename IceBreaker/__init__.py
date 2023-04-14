from flask import Flask, render_template, request, session, redirect
from flask_socketio import SocketIO, emit
from flask_session import Session
import uuid
from time import sleep

app = Flask(__name__)
app.secret_key = "asdf1234" #TODO:CHANGE THIS TO SOMETHING MORE SECURE
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
socketio = SocketIO(app, manage_session=False)

@app.route('/favicon.ico')
def favicon():
    return redirect('/static/favicon.ico')

@app.errorhandler(404)
def page_not_found(e):
    print(request.url)
    return redirect("/")

@app.route('/chat', methods=['GET'])
def chat():
    if 'user_id' not in session: #TODO: Check if user is paired
        return redirect('/')
    else:
        print("#"*80)
        print(session)
        return render_template('chat.html', data={'user_id': session['user_id'], 'user_name': session['user_name'], 'partner_id': session['partner_id'], 'partner_name': session['partner_name']})

@socketio.on('pair')
def pair():
    if 'user_id' not in session:
        return redirect('/')
    else:
        print("#"*80)
        print("Otrzymałem żądanie od użytkownika: %s. Wyszukuje pasującej pary" % session['user_id'])
        session['partner_id'] = "123"
        session['partner_name'] = "ABC" #TODO: Wyszukaj pasującą parę
        session.modified = True
        print(session)
        # return render_template('chat.html', data={'user_id': session['user_id'], 'user_name': session['user_name'], 'partner_id': session['partner_id'], 'partner_name': session['partner_name']})
        # return redirect('/chat')
        emit('paired', data={'user_id': session['user_id'], 'user_name': session['user_name'], 'partner_id': session['partner_id'], 'partner_name': session['partner_name']})
    
@app.route('/wait', methods=['GET'])
def wait():
    if 'user_id' not in session:
        return redirect('/')
    else:
        print("#"*80)
        print(session)
        return render_template('wait.html', message="We are looking for someone to talk to you. Please wait...", data={'user_id': session['user_id'], 'user_name': session['user_name'], 'partner_id': session['partner_id'], 'partner_name': session['partner_name']})
    
#Handle form request
@app.route('/submit-form/', methods=['POST'])
def handle_form():
    print("#"*80)
    print("user_id: %s" % session['user_id'])
    print('user_id' in session)
    if 'user_id' in session:
        print("Submitted form with name: %s" % request.form['name'])
        session['user_name'] = request.form['name']
    return redirect('/wait')

@app.route('/', methods=['GET'])
def index():
    if 'user_id' not in session:
        session['user_id'] = uuid.uuid4().hex
        session['user_name'] = None
        session['partner_id'] = None
        session['partner_name'] = None
        return render_template('index.html', data={'user_id': session['user_id'], 'user_name': session['user_name'], 'partner_id': session['partner_id'], 'partner_name': session['partner_name']})
    else:
        print("user_id: %s" % session['user_id'])
        return render_template('index.html', data={'user_id': session['user_id'], 'user_name': session['user_name'], 'partner_id': session['partner_id'], 'partner_name': session['partner_name']})
        # return redirect('/wait')
        # return render_template('index.html', message="Welcome %s" % session['user_name'])

if __name__ == '__main__':
    socketio.run(app)