import sys
from requests.exceptions import ConnectionError
from socketIO_client import SocketIO
from socketIO_client.transports import WebsocketTransport 

socket = None

def on_connect():
    print('connected to sio-server')
    print('Sending hello to sio-server')
    socket.emit('message', 'hello');

def on_disconnect():
    print('disconnected from sio-server')

def on_reconnect():
    print('reconnecting to sio-server')

def on_unicastedFrame(*args):
    print('on_message', args)
                                        
if __name__ == '__main__' :
    if len(sys.argv) < 5 :
        # Testing against the server launched by "https://github.com/genxium/socket.io-redis-express4-react16-simple-starter/blob/master/backend/api.js" which uses "socket.io core v1.7.2" -- which is in turn used by "pomelo v2.2.5".
        print "\nUsage:\n\nbashshell> pipenv run python %s <host> <port> <playerId> <roomid>" %(sys.argv[0])
        sys.exit(1)

    host = sys.argv[1]
    port = sys.argv[2]
    playerId = sys.argv[3]
    roomid = sys.argv[4]
    
    try:
        socket = SocketIO(host, port, 
                # What's called "path" in socketio-server-api v1.x.x(including v1.7.2) options is here called "resource", e.g. by default "/socket.io".
                resource="sio", 
                transports=[WebsocketTransport],
                params={
                    'playerId': playerId, 
                    'roomid': roomid
                },
                wait_for_connection=False)
        socket.on('connect', on_connect)
        socket.on('disconnect', on_disconnect)
        socket.on('reconnect', on_reconnect)
        socket.on('unicastedFrame', on_unicastedFrame)
        socket.wait()
    except ConnectionError:
        print('The sio-server is down. Try again later.')
    except KeyboardInterrupt:
        sys.exit(0)
