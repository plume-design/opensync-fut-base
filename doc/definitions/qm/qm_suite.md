# QM testing

## Overview

QM test suite tests the Queue Manager, responsible for managing all MQTT messages from other OpenSync processes. It
tries not to drop any messages even if uplink connectivity drops (e.g., transient failure of backhaul connectivity, ISP
blackout, etc). The messages are encoded using Google protobuf. Multiple messages within a reporting interval are
merged into a single message. Other managers communicate with QM over a Unix socket.
