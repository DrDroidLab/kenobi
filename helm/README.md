## Helm setup instructions for kenobi

### Go to helm directory and choose a namespace of your choice 

```bash
cd helm
export NAMESPACE=deployment
```

### Switch local context to the k8s cluster you want to deploy
``` shell
kubectl config use-context <cluster_identifier>
```

### Setup secrets (for credentials)
Add credentials/keys for Postgres DB, AWS & Clickhouse DB by running this command from the ```helm``` directory
``` shell
helm upgrade secrets --install --namespace $NAMESPACE --create-namespace --values ./values/secret-value.yaml ./charts/secrets
```

### Setup 

### Create External Services
For all resources not managed within the cluster, you'll need to create them outside and setup their external services


### 1. Postgres DB
Add the database hostname in ```external/database.yaml``` and run the following command from the ```helm``` directory
```shell
kubectl apply -f ./external/database.yaml --namespace $NAMESPACE
```

### 2. Redis
Add the Redis hostname in ```external/redis.yaml``` and run the following command from the ```helm``` directory
```shell
kubectl apply -f ./external/redis.yaml --namespace $NAMESPACE
```

### 3. Clickhouse
Add the Clickhouse hostname in ```external/clickhouse.yaml``` and run the following command from the ```helm``` directory
```shell
kubectl apply -f ./external/clickhouse.yaml --namespace $NAMESPACE
```

### 4. Kafka
Setup a Kafka cluster and run these commands to create 4 kafka topics in it


```shell
kafka-topics.sh --create --topic raw-events --partitions 10 --replication-factor 1 --bootstrap-server localhost:9092

kafka-topics.sh --create --topic raw_monitor_transactions --partitions 10 --replication-factor 1 --bootstrap-server localhost:9092

kafka-topics.sh --create --topic processed_monitor_transactions_clickhouse --partitions 10 --replication-factor 1 --bootstrap-server localhost:9092

kafka-topics.sh --create --topic processed_events_clickhouse --partitions 10 --replication-factor 1 --bootstrap-server localhost:9092
```

Check all topics are created
``` shell
kafka-topics.sh --list --bootstrap-server localhost:9092
```

Add the kafka broker hostname in ```external/kafka.yaml``` and run the following command from the ```helm``` directory
``` shell
kubectl apply -f ./external/kafka.yaml --namespace $NAMESPACE
```

> [!NOTE]
> For prototyping, use the [service.docker-compose.yaml](/helm/services.docker-compose.yaml) to setup these 4 dependencies in a dedicated virtual machine. Then you can setup a load balancer on top it for the following ports - 8123, 5432, 9092, 6379 and put them as services.

### Deploy Code
Setup env variables for the script to pickup the docker images from. Use the LTS images published by Doctor Droid. 
``` shell
export IMAGE='public.ecr.aws/y9s1f3r5/drdroid/prototype:latest'
export IMAGE_WEB='public.ecr.aws/y9s1f3r5/drdroid/webvault:latest'
```

Run the following command from repository's root directory to deploy the kenobi containers
``` shell
./scripts/upgrade_prototype.sh
```

### Setup Ingress
Run the following command from the ```helm``` directory to create the networking for the cluster
``` shell
kubectl apply -f ./external/ingress.yaml --namespace $NAMESPACE
```

### Retrieve the deployed endpoint
Run the following command from the ```helm``` directory to get the web external endpoint for kenobi
``` shell
kubectl get svc webvault -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].hostname}:{.spec.ports[0].port}'
```

A superuser with the following credentials will be auto created for you to get started
``` shell
Email: admin@drdroid.io
Password: password
```

