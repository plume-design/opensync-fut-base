#!/bin/bash

envsubst '$OPENSYNC_ROOT' < /etc/nginx/sites-available/default.template > /tmp/default.nginx
sudo cp /tmp/default.nginx /etc/nginx/sites-available/default
sudo service nginx restart

while true
do
  echo "Starting app.py"
  sudo service nginx start
  python3 /var/www/app/app.py
  echo "Crashed app.py"
  sleep 1
done
