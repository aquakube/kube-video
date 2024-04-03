# Controller


The video controller is responsible for managing the Video custom resourece.
The controller can create, update or delete instances of those custom resources as needed when events are received over kafka.

The operator, on the other hand, is a pattern for extending Kubernetes to automate the management of complex applications or infrastructure.
The operator will manage the deployment and service for the video resource.


## Run

```
KAFKA_BROKERS=localhost:9092 \
KAFKA_CONSUME_TOPIC=aquavid.events \
KAFKA_CONSUME_CLIENT_PREFIX=video-controller-client- \
KAFKA_CONSUME_GROUP_ID=video-controller \
CLOUDEVENT_SCHEMA_PATH=apps/controller/src/schemas/cloudEvent-1.0.0.json \
AQUAVID_SUBSCRIPTION_EVENT_SCHEMA_PATH=apps/controller/src/schemas/aquavidSubscriptionEvent-1.0.0.json \
AQUAVID_URL=http://aquavid.video.svc.cluster.local \
MINIMUM_TEARDOWN_DELAY=20s \
INACTIVITY_THRESHOLD=10m \
RECONCILIATION_INTERVAL=1m \
CAMERA_MAP_PATH=apps/controller/bin/camera-map.json \
python3 apps/controller/src/main.py
```