# Servers

This client is to be tested against [a specific sio-server](https://github.com/genxium/socket.io-redis-express4-react16-simple-starter) and [a specific pomelo-server](https://github.com/genxium/single-pomelo-backend-server) for feasibility verification, in that order.

# Prerequisites
Install [pipenv](https://docs.pipenv.org/).

```
user@proj-root> pipenv install
```

However to make use of the Locust task runner, you're stil suggested to install all dependencies "globally" via pip.

```
user@proj-root> pip install locust 
user@proj-root> pip install socketIO_client
user@proj-root> pip install requests 
```

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
