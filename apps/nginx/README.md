# Nginx

This nginx server uses the nginx-rtmp module for ingesting RTMP and delivering HLS for live video playback on aquavid UI.
NOTE:  The video pods push RTMP to this service, but they are also reaching out for stats to determine if the video pipeline is working.

## local playback ###
http://<node_ip>:30150/stat
http://<node_ip>:30150/api/hls/v1/avalon-koa-dev-c2-bow.m3u8


### production playback ###
Video will be requested from video.<operatingsite>.aquakube.com
HLS will be delivered vai this service at the domain hls.<operatingsite>.aquakube.com
Go see the <operatingsite>_resources repository to view ingress resources
