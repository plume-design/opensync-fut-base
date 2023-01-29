#!/bin/bash

sudo bash -c "echo '192.168.200.1 fut.opensync.io' >> /etc/hosts" &&
    echo "fut.opensync.io added to /etc/hosts/ file at IP 192.168.200.1" ||
    echo "WARNING: failed to add fut.opensync.io to /etc/hosts/ file at IP 192.168.200.1"

sudo chown plume:plume -R /var/www/app/
./butterfly.sh > /dev/null 2>&1 &
./app.sh > /tmp/fut.log 2>&1 &
