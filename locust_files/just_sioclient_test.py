import sys
from requests.exceptions import ConnectionError
from socketIO_client import SocketIO
from socketIO_client.transports import WebsocketTransport 

from locust import Locust,TaskSet,task
import baseoper 

baseoper.init()
socket = None

def on_connect():
  print('connected to sio-server')
  '''
  print('Sending hello to sio-server')
  socket.emit('message', 'hello');
  '''

def on_disconnect():
  print('disconnected from sio-server')

def on_reconnect():
  print('reconnecting to sio-server')

def on_unicastedFrame(*args):
  print('on_message', args)
                                        
def connect_to_sio_server(lct):
  fp = baseoper.get_single_random_player()
  playerId = fp[0]
  roomid = fp[1]

  sio_server = baseoper.get_sio_server_host_port()
  host = sio_server[0]
  port = sio_server[1]

  try:
      socket = SocketIO(
              host, 
              port, 
              resource="sio", 
              transports=[WebsocketTransport],
              params={
                  'playerId': playerId, 
                  'roomid': roomid
              },
              wait_for_connection=False
      )
      socket.on('connect', on_connect)
      socket.on('disconnect', on_disconnect)
      socket.on('reconnect', on_reconnect)
      socket.on('unicastedFrame', on_unicastedFrame)
      socket.wait()
  except ConnectionError:
      print('The sio-server is down. Try again later.')
  except KeyboardInterrupt:
      sys.exit(0)

class SimplestConnectionEstablishmentTaskSet(TaskSet):
  tasks = [connect_to_sio_server]

class TaskLocust(Locust):
  min_wait = 0
  max_wait = 1000
  task_set = SimplestConnectionEstablishmentTaskSet
