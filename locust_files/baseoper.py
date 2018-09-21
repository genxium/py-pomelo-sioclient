import sqlite3
import random
import ConfigParser
import os

def init():
  global _sio_server 
  cf = ConfigParser.ConfigParser()
  currentDir = os.path.dirname(__file__) + "/" 
  cf.read(currentDir + "../config/ext_service.ini")
  _sio_server = (cf.get("sio-server", "host"), cf.get("sio-server", "port"))
  global _test_player_list
  global _tot_test_player_count
  conn = sqlite3.connect(currentDir + "../config/preconfigured.sqlite")
  c = conn.cursor()
  _tot_test_player_count = c.execute("SELECT COUNT(id) FROM player_test").fetchone()[0]
  _test_player_list = c.execute("SELECT id,roomid FROM player_test").fetchall()
  conn.commit()
  conn.close()

def get_single_random_player():
  idx = random.randint(1, _tot_test_player_count - 1)
  return _test_player_list[idx]

def get_sio_server_host_port():
  return _sio_server
