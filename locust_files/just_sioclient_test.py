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

  def setup(self):
    print("SimplestConnectionEstablishmentTaskSet.setup completed. I'm called only once for all locusts (NOT `once per locust` or `once per task_set` or `once per locust*task_set`) during the lifetime of the current OS process.")

  def on_start(self):
    print("SimplestConnectionEstablishmentTaskSet.on_start for player.id == %s to roomid == %s." % (self.locust.playerId, self.locust.roomid))
    '''
    The following `self.client.wait()` is responsible for holding `self.client` aware of the callback events, e.g. "on_connect", "on_disconnect" etc INDEFINITELY except for interrupted by "locust.exception.StopLocust" or "gevent.GreenletExit".
    '''
    self.client.wait()   
    print("SimplestConnectionEstablishmentTaskSet instance for player.id == %s to roomid == %s sioclient is initialized and awaiting callback events." % (self.locust.playerId, self.locust.roomid)) 

  def on_stop(self):
    print("SimplestConnectionEstablishmentTaskSet.on_stop for player.id == %s to roomid == %s." % (self.locust.playerId, self.locust.roomid))

  def teardown(self):
    print("SimplestConnectionEstablishmentTaskSet all instances have been torn down. I'm called only once for all locusts (NOT `once per locust` or `once per task_set` or `once per locust*task_set`) during the lifetime of the current OS process.") 


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

  def _init_sio_client(self):
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
      self.client.on('message', self.on_message)
    except ConnectionError:
      print("SimplestConnectionEstablishmentPlayer instance for player.id == %s to roomid == %s. The sio-server is down, try again later." % (self.playerId, self.roomid))
    except KeyboardInterrupt:
      raise GreenletExit()

  def on_connect(self):
    print('SimplestConnectionEstablishmentPlayer instance for player.id == %s to roomid == %s, connected to sio-server.' % (self.playerId, self.roomid))

  def on_disconnect(self):
    print('SimplestConnectionEstablishmentPlayer instance for player.id == %s to roomid == %s, disconnected from sio-server.' % (self.playerId, self.roomid))
    raise StopLocust()

  def on_message(self, *args):
    print('SimplestConnectionEstablishmentPlayer instance for player.id == %s to roomid == %s, on_message %s.' % (self.playerId, self.roomid, args))

  def __init__(self, *args, **kwargs):
    '''
    Note that `self.setup` will run within the immediately following invocation if "False == Locust._setup_has_run", see https://github.com/locustio/locust/blob/master/locust/core.py for details (Locust v0.9).
    '''
    super(SimplestConnectionEstablishmentPlayer, self).__init__(*args, **kwargs)
    fp = baseoper.get_single_random_player()
    self.playerId = fp[0]
    self.roomid = fp[1]

    sio_server = baseoper.get_sio_server_host_port()
    self.host = sio_server[0]
    self.port = int(sio_server[1])
    '''
    The call to `self._init_sio_client()` SHOULDN'T be put into `"self.setup" or "Locust.setup"` which runs only once for "all locusts spawned by the current OS process", due to "Locust._setup_has_run" being a class-static-variable (unless otherwise hacked via `self._setup_has_run` which is unnecessary), see https://github.com/locustio/locust/blob/master/locust/core.py for details (Locust v0.9).

    Same argument holds for "Locust.teardown", "TaskSet.setup" and "TaskSet.teardown".
    '''
    self._init_sio_client()

  def setup(self):
    print("SimplestConnectionEstablishmentPlayer.setup completed. I'm called only once for all locusts (NOT `once per locust`) during the lifetime of the current OS process.")

  def teardown(self):
    print("SimplestConnectionEstablishmentPlayer all instances have been torn down. I'm called only once for all locusts (NOT `once per locust`) during the lifetime of the current OS process.") 

