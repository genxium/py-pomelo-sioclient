# -*- coding:utf-8 -*-
import sys
import time
from requests.exceptions import ConnectionError
from socketIO_client import SocketIO

from locust import Locust, TaskSet, task, events
from locust.exception import StopLocust
from gevent import GreenletExit
import baseoper 

'''
Major references
- https://docs.locust.io/en/stable/writing-a-locustfile.html#setups-teardowns-on-start-and-on-stop
- https://docs.locust.io/en/stable/testing-other-systems.html#
- https://github.com/locustio/locust/blob/master/examples/dynamice_user_credentials.py
- For how to correctly stop a `TaskSet` and a `Locust`, respectively.
    - https://github.com/locustio/locust/blob/master/locust/core.py, keyword "task_set_instance.run" & "StopLocust"
    - https://github.com/locustio/locust/blob/master/locust/runners.py, keyword "locust().run" & "GreenletExit"
'''
baseoper.init()

class SimplestConnectionEstablishmentTaskSet(TaskSet):
  def __init__(self, *args, **kwargs):
    super(SimplestConnectionEstablishmentTaskSet, self).__init__(*args, **kwargs)
    print("SimplestConnectionEstablishmentTaskSet instance for player.id == %s to roomid == %s, __init__ has just started..." % (self.locust.playerId, self.locust.roomid))

  def setup(self):
    print("SimplestConnectionEstablishmentTaskSet instance for player.id == %s to roomid == %s, setup has just started..." % (self.locust.playerId, self.locust.roomid))

  def on_start(self):
    print("SimplestConnectionEstablishmentTaskSet instance has been started for player.id == %s to roomid == %s." % (self.locust.playerId, self.locust.roomid))

  def on_stop(self):
    print("SimplestConnectionEstablishmentTaskSet instance is stopped for player.id == %s to roomid == %s." % (self.locust.playerId, self.locust.roomid))

  def teardown(self):
    print("SimplestConnectionEstablishmentTaskSet instance has been torn down for player.id == %s to roomid == %s." % (self.locust.playerId, self.locust.roomid)) 


  @task(1)
  def action(self):
    try:
      self.client.emit('message', 'hello')
    except ConnectionError:
      print("Connection error for player.id == %s to roomid == %s. Stopping the SimplestConnectionEstablishmentTaskSet instance..." % (self.locust.playerId, self.locust.roomid))
      raise StopLocust()
    except KeyboardInterrupt:
      print("Keyboard interrupted for player.id == %s to roomid == %s. Stopping the SimplestConnectionEstablishmentTaskSet instance..." % (self.locust.playerId, self.locust.roomid))
      raise StopLocust()
    except Exception:
      print("Unknown error for player.id == %s to roomid == %s. Stopping the SimplestConnectionEstablishmentTaskSet instance..." % (self.locust.playerId, self.locust.roomid))
      raise StopLocust()

class SimplestConnectionEstablishmentPlayer(Locust):
  min_wait = 1000
  max_wait = 1000
  task_set = SimplestConnectionEstablishmentTaskSet

  def on_connect(self):
    print('SimplestConnectionEstablishmentPlayer instance for player.id == %s to roomid == %s, connected to sio-server.' % (self.playerId, self.roomid))

  def on_disconnect(self):
    print('SimplestConnectionEstablishmentPlayer instance for player.id == %s to roomid == %s, disconnected from sio-server.' % (self.playerId, self.roomid))

  def on_unicastedFrame(self, *args):
    print('SimplestConnectionEstablishmentPlayer instance for player.id == %s to roomid == %s, on_message %s.' % (self.playerId, self.roomid, args))

  def __init__(self, *args, **kwargs):
    fp = baseoper.get_single_random_player()
    self.playerId = fp[0]
    self.roomid = fp[1]

    sio_server = baseoper.get_sio_server_host_port()
    self.host = sio_server[0]
    self.port = sio_server[1]
    print("SimplestConnectionEstablishmentPlayer instance is just initialized, about to connect to server %s:%s for player.id == %s to roomid == %s." % (self.host, self.port, self.playerId, self.roomid))
    self.client = None
    super(SimplestConnectionEstablishmentPlayer, self).__init__(*args, **kwargs) # Note that `self.setup` will run hereafter.

  def setup(self):
    print("SimplestConnectionEstablishmentPlayer instance for player.id == %s to roomid == %s, setup has just started..." % (self.playerId, self.roomid))
    try:
      self.client = SocketIO(
                              self.host, self.port, 
                              resource='sio', 
                              transports=['websocket'],
                              params={
                                  'userid': self.playerId, 
                                  'roomid': self.roomid
                              },
                              wait_for_connection=False # Disabling auto-reconnection.
                    )
      '''
      The NodeJs server MUST be using `"socket.io": "1.7.2"` or an error complaining

      "
      ... socketIO_client.__init__, in _get_engineIO_session ...
      ... transport.recv_packet() ...
      "
      
      would be thrown here.
      '''
      self.client.on('connect', self.on_connect)
      self.client.on('disconnect', self.on_disconnect)
      self.client.on('unicastedFrame', self.on_unicastedFrame)
      self.client.wait(10) # Don't use just `self.client.wait()` or the current `locust/gevent.Greenlet` will block here forever.  
      print("SimplestConnectionEstablishmentPlayer instance for player.id == %s to roomid == %s sioclient is initialized and awaiting callback events." % (self.playerId, self.roomid)) 
    except ConnectionError:
      print("SimplestConnectionEstablishmentPlayer instance for player.id == %s to roomid == %s. The sio-server is down, try again later." % (self.playerId, self.roomid))
    except KeyboardInterrupt:
      raise GreenletExit()

  def teardown(self):
    print("SimplestConnectionEstablishmentPlayer instance for player.id == %s to roomid == %s has been torn down." % (self.playerId, self.roomid)) 

