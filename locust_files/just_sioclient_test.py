# -*- coding:utf-8 -*-
import sys
import time
from requests.exceptions import ConnectionError
from socketIO_client import SocketIO

from locust import Locust, TaskSet, task, events
from locust.exception import StopLocust
from gevent import GreenletExit
from gevent import monkey
import gevent
import baseoper 

monkey.patch_all() # Make Gevent compatible with some blocking system calls, see http://www.gevent.org/api/gevent.monkey.html for details.

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
    print("SimplestConnectionEstablishmentTaskSet.on_start for player.id == %s to room_id == %s." % (self.locust.player_id, self.locust.room_id))
    '''
    The following `self.client.wait()` is responsible for holding `self.client` aware of the callback events, e.g. "on_connect", "on_disconnect" etc INDEFINITELY except for interrupted by "locust.exception.StopLocust" or "gevent.GreenletExit". It's blocking if not wrapped by gevent, see https://github.com/invisibleroads/socketIO-client/blob/master/socketIO_client/__init__.py and https://github.com/invisibleroads/socketIO-client/blob/master/socketIO_client/logs.py for details about its use of "looping generator & yield" (socketIO_client v0.7.2).
    '''
    def on_sio_client_wait_exception(glt):
      '''
      This is still within the "spawned greenlet from main locust". 
      
      See http://www.gevent.org/api/gevent.greenlet.html#gevent.Greenlet.link_exception and http://www.gevent.org/api/gevent.greenlet.html#gevent.greenlet.greenlet for details.
      '''
      print("Exception of the non_blocking_waiting of the sioclient caught for player.id == %s to room_id == %s." % (self.locust.player_id, self.locust.room_id))
      raise StopLocust

    non_blocking_waiting = gevent.spawn(self.client.wait).link_exception(on_sio_client_wait_exception) 
    print("SimplestConnectionEstablishmentTaskSet instance for player.id == %s to room_id == %s sioclient is initialized and awaiting callback events." % (self.locust.player_id, self.locust.room_id)) 

  def on_stop(self):
    print("SimplestConnectionEstablishmentTaskSet.on_stop for player.id == %s to room_id == %s." % (self.locust.player_id, self.locust.room_id))

  def teardown(self):
    print("SimplestConnectionEstablishmentTaskSet all instances have been torn down. I'm called only once for all locusts (NOT `once per locust` or `once per task_set` or `once per locust*task_set`) during the lifetime of the current OS process.") 


  @task(1)
  def action(self):
    try:
      self.client.emit('message', 'hello')
    except ConnectionError:
      print("[ACTIVELY DISCONNECTING] SimplestConnectionEstablishmentTaskSet connection error for player.id == %s to room_id == %s." % (self.locust.player_id, self.locust.room_id))
      self.client.disconnect() # Will trigger `self.locust.on_disconnect` to proceed.
    except Exception:
      print("[ACTIVELY DISCONNECTING] SimplestConnectionEstablishmentTaskSet unknown error for player.id == %s to room_id == %s." % (self.locust.player_id, self.locust.room_id))
      self.client.disconnect() # Will trigger `self.locust.on_disconnect` to proceed.

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
                                  'userid': self.player_id, 
                                  'roomid': self.room_id
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
      print("SimplestConnectionEstablishmentPlayer instance for player.id == %s to room_id == %s. The sio-server is down, try again later." % (self.player_id, self.room_id))
      raise GreenletExit()
    except KeyboardInterrupt:
      raise GreenletExit()

  def on_connect(self):
    print('SimplestConnectionEstablishmentPlayer instance for player.id == %s to room_id == %s, connected to sio-server.' % (self.player_id, self.room_id))

  def on_disconnect(self):
    '''
    A subtlety to be concerned here. 
    '''
    if (True == self.client._should_stop_waiting()):
      # If the execution reaches here by actively calling `self.client.disconnect()`, then one finds "True == self.client._should_stop_waiting() == self.client._wants_to_close".
      print('[ACTIVELY DISCONNECTED] SimplestConnectionEstablishmentPlayer for player.id == %s to room_id == %s.' % (self.player_id, self.room_id))
      raise StopLocust() # This is usually within the "main locust".
    else:
      # If the execution reaches here passively within `self.client.wait()`, then one finds "False == self.client._should_stop_waiting() == self.client._wants_to_close", and should help terminate the loop in the spawned `self.client.wait()`. See https://github.com/invisibleroads/socketIO-client/blob/master/socketIO_client/__init__.py for details (socketIO_client v0.7.2).
      print('[PASSIVELY DISCONNECTED] SimplestConnectionEstablishmentPlayer for player.id == %s to room_id == %s.' % (self.player_id, self.room_id))
      self.client._close()
      '''
      DON'T raise `GreenletExit` here! 

      Quoted from http://www.gevent.org/api/gevent.greenlet.html#gevent.GreenletExit for "gevent v1.3.7.dev0".  

      "
      A special exception that kills the greenlet silently.

      When a greenlet raises GreenletExit or a subclass, the traceback is not printed and the greenlet is considered successful. The exception instance is available under value property as if it was returned by the greenlet, not raised.
      "
      '''
      raise StopLocust() # This is usually within the "spawned greenlet from main locust" and will be caught by `link_exception` for proceeding.

  def on_message(self, *args):
    print('SimplestConnectionEstablishmentPlayer instance for player.id == %s to room_id == %s, on_message %s.' % (self.player_id, self.room_id, args))

  def __init__(self, *args, **kwargs):
    '''
    Note that `self.setup` will run within the immediately following invocation if "False == Locust._setup_has_run", see https://github.com/locustio/locust/blob/master/locust/core.py for details (Locust v0.9).
    '''
    super(SimplestConnectionEstablishmentPlayer, self).__init__(*args, **kwargs)
    fp = baseoper.get_single_random_player()
    self.player_id = fp[0]
    self.room_id = fp[1]

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

