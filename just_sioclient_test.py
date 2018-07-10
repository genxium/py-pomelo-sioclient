import sys
from requests.exceptions import ConnectionError
from socketIO_client import SocketIO

def on_connect():
    print('connected to sio-server')

def on_disconnect():
    print('disconnected from sio-server')

def on_reconnect():
    print('reconnecting to sio-server')

def on_message(*args):
    print('on_message', args)

if __name__ == '__main__' :
    if len(sys.argv) < 5 :
        # Testing against the server launched by "https://github.com/genxium/socket.io-redis-express4-react16-simple-starter/blob/master/backend/api.js".
        print "\nUsage:\n\nbashshell> pipenv run python %s <host> <port> <playerId> <roomid>" %(sys.argv[0])
        sys.exit(1)

    host = sys.argv[1]
    port = sys.argv[2]

    playerId = sys.argv[3]
    roomid = sys.argv[4]
    try:
        socket = SocketIO(host, port, 
                # What's called "path" in socketio-server-api v1.x & v2.x options is here called "resource", e.g. by default "/socket.io".
                resource="sio", 
                params={'playerId': playerId, 'roomid': roomid},
                wait_for_connection=False)
        socketIO.on('connect', on_connect)
        socketIO.on('disconnect', on_disconnect)
        socketIO.on('reconnect', on_reconnect)
        socketIO.on('message', on_message)
        socket.wait()
    except ConnectionError:
        print('The sio-server is down. Try again later.')
    except KeyboardInterrupt:
        sys.exit(0)
