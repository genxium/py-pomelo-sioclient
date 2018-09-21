# Servers

This client is to be tested against [a specific sio-server](https://github.com/genxium/nodejs-cluster-prac) and [a specific pomelo-server](https://github.com/genxium/single-pomelo-backend-server) for feasibility verification, in that order.

## More about testing against PM2
A glitch of [this Python library socketIO-client](https://github.com/invisibleroads/socketIO-client) is that it doesn't respect the client option `transports=['websocket']`, i.e. it tries to make an xhr-polling before upgrading to websocket anyway, by 2018-08-26. 

This isn't a problem when using some customized reverse-proxying & load-balancing approaches such as [NodeJsCluster](https://github.com/genxium/nodejs-cluster-prac) or [that of Pomelo](https://shimo.im/doc/h5nNMqIET6Ik1BBn/). However it's not compatible with the default reverse-proxying & load-balancing behaviour with PM2, i.e. would trigger [a "Session ID Unknown" issue](https://github.com/socketio/socket.io/issues/1982). There seems to be [a pull request to the rescue](https://github.com/invisibleroads/socketIO-client/pull/142) but I haven't verified it yet.   

# Prerequisites
Install [pipenv](https://docs.pipenv.org/).

```
user@proj-root> pipenv install
```

However to make use of the Locust task runner, you're stil suggested to install all dependencies "globally" via pip.

```
user@~> pip install "locustio>=0.9" 
user@~> pip install socketIO_client
user@~> pip install requests 
```

Make sure that you've installed `locustio v0.9(+)` by 
```
user@~> locust --version 
```
in shell.


# Running standalone with necessary params
```
user@proj-root> pipenv run python just_sioclient_test.py <host> <port> <playerId> <roomid> 
```

Or if you're not using pipenv and have installed the dependencies "globally"

```
user@proj-root> python just_sioclient_test.py <host> <port> <playerId> <roomid> 
```

# Running with Locust 
Without custom NodeJs wrapper.
```
user@proj-root> locust -f locust_files/just_sioclient_test.py --no-web -c1 -r1 
```

With custom NodeJs wrapper.
```
user@proj-root> node ./locust_launcher.js --totalUsers 1 -locustFile locust_files/just_sioclient_test.py --csvDirPath ~/myStressingReports/ 
```
