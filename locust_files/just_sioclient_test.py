# -*- coding:utf-8 -*-
import sys
from requests.exceptions import ConnectionError
from socketIO_client import SocketIO

from locust import Locust, TaskSet, task
import baseoper 

'''
Major references
- https://github.com/locustio/locust/blob/master/examples/dynamice_user_credentials.py
- https://github.com/locustio/locust/blob/master/examples/custom_xmlrpc_client/xmlrpc_locustfile.py
'''
baseoper.init()

class SimplestConnectionEstablishmentTaskSet(TaskSet):
  def on_start(self):
    try:
      self.client.wait()
    except ConnectionError:
      print("The sio-server is down for player.id == %s to roomid == %s. Try again later." % (self.playerId, self.roomid))
    except KeyboardInterrupt:
      sys.exit(0)

  @task(1)
  def action(self):
    self.client.emit('message', 'hello')

class SimplestConnectionEstablishmentPlayer(Locust):
  min_wait = 100
  max_wait = 1000
  task_set = SimplestConnectionEstablishmentTaskSet

  def __init__(self):
    fp = baseoper.get_single_random_player()
    self.playerId = fp[0]
    self.roomid = fp[1]

    sio_server = baseoper.get_sio_server_host_port()
    host = sio_server[0]
    port = sio_server[1]

    try:
      self.client = SocketIO(
                              host, port, 
                              resource='sio', 
                              transports=['websocket'],
                              params={
                                  'playerId': self.playerId, 
                                  'roomid': self.roomid
                              },
                              wait_for_connection=False
                    )

      def on_connect():
        print('connected to sio-server')

      def on_disconnect():
        print('disconnected from sio-server')

      def on_reconnect():
        print('reconnecting to sio-server')

      def on_unicastedFrame(*args):
        print('on_message', args)

      self.client.on('connect', on_connect)
      self.client.on('disconnect', on_disconnect)
      self.client.on('reconnect', on_reconnect)
      self.client.on('unicastedFrame', on_unicastedFrame)
    except ConnectionError:
      print("The sio-server is down for player.id == %s to roomid == %s. Try again later." % (self.playerId, self.roomid))
    except KeyboardInterrupt:
      sys.exit(0)
