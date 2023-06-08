from IceBreaker import create_app, socketio
import logging

app = create_app()

if __name__ == '__main__':
    socketio.run(app, debug=True)