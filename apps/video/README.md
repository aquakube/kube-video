# Video

This application will run the provided video pipeline

## Run

```
DEBUG=False \
KUBERNETES_NAMESPACE_NAME=fieldRef(v1:metadata.namespace) \
KUBERNETES_POD_NAME=fieldRef(v1:metadata.name) \
KUBERNETES_POD_UID=fieldRef(v1:metadata.uid) \
NAME=avalon-koa-dev-eagle180-02 \
OTEL_SERVICE_NAME=aavalon-koa-dev-eagle180-02 \
OTEL_EXPORTER_OTLP_METRICS_ENDPOINT=10.0.9.21:4317 \
OTEL_EXPORTER_OTLP_METRICS_INSECURE=true \
OTEL_EXPORTER_OTLP_METRICS_PROTOCOL=grpc \
OTEL_EXPORTER_OTLP_METRICS_TIMEOUT=2500 \
OTEL_METRICS_EXPORTER=otlp,console \
OTEL_METRIC_EXPORT_INTERVAL=5000 \
OTEL_METRIC_EXPORT_TIMEOUT=2500 \
PIPELINE="rtspsrc location='rtsp://10.0.9.105/user=admin_password=tlJwpbo6_channel=1_stream=0.sdp?real_stream' latency=0 drop-on-latency=true udp-reconnect=true ntp-sync=true do-rtsp-keep-alive=true protocols='udp' timeout=10000000 ! rtph264depay ! h264parse ! flvmux streamable=true ! rtmpsink location=rtmp://nginx.video.svc.cluster.local:1935/live/avalon-koa-dev-eagle180-02" \
NGINX_STATS_URL=http://10.0.9.21:30150/stat \
MONITOR_STARTUP_DELAY=20 \
MONITOR_POLL_INTERVAL=20 \
VERSION=0.0.0 \
python3 apps/streamer/src/main.py
```
