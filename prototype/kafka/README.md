# Local kafka setup
Run the following commands in order to start all services in the correct order:

# Start the ZooKeeper service
```shell
bin/zookeeper-server-start.sh config/zookeeper.properties
```
Open another terminal session and run:

# Start the Kafka broker service
```shell
bin/kafka-server-start.sh config/server.properties
```
Once all services have successfully launched, you will have a basic Kafka environment running and ready to use.