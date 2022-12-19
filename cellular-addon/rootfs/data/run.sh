#!/usr/bin/with-contenv bashio

INTERVAL=$(bashio::config 'interval')

echo "Sixfab Cellular add-on started."

while true; do
    echo "Checking configuration..."
    python3 -m configure_modem
    sleep $INTERVAL
done