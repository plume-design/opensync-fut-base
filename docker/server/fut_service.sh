#!/bin/bash

# This entry allows the gatekeeper to be tested from the server directly and enhances testability
sudo bash -c "echo '127.0.0.1 fut.opensync.io' >> /etc/hosts" &&
    echo "fut.opensync.io added to /etc/hosts/ file at IP 127.0.0.1" ||
    echo "WARNING: failed to add fut.opensync.io to /etc/hosts/ file at IP 127.0.0.1"

envsubst '$OPENSYNC_ROOT' < /etc/nginx/sites-available/default.template > /tmp/default.nginx
sudo cp /tmp/default.nginx /etc/nginx/sites-available/default
sudo service nginx restart

while true
do
    echo "Starting gatekeeper.py"
    sudo service nginx start
    python3 /var/www/gatekeeper/gatekeeper.py
    echo "Crashed gatekeeper.py"
    sleep 1
done
