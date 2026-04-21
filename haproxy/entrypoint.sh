#!/bin/sh
set -e

CERT_DIR="/etc/letsencrypt/live/led-board.frankhereford.com"
HAPROXY_PEM="/certs/haproxy.pem"

mkdir -p /certs
cat "$CERT_DIR/fullchain.pem" "$CERT_DIR/privkey.pem" > "$HAPROXY_PEM"
chmod 600 "$HAPROXY_PEM"

exec haproxy -f /usr/local/etc/haproxy/haproxy.cfg -db
