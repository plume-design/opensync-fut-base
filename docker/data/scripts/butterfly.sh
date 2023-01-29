#!/bin/bash

while true
do
  echo "Starting butterfly.server.py"
  echo "$SSH_AUTH_SOCK" > /tmp/.auth_sock
  butterfly.server.py --i_hereby_declare_i_dont_want_any_security_whatsoever --host=0.0.0.0 --port=57575 --unsecure
  echo "Crashed butterfly.server.py"
  sleep 1
done
