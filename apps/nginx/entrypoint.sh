#!/usr/bin/env sh
set -eu

envsubst '${OPERATINGSITE}' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf

exec "$@"