# // Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# // SPDX-License-Identifier: MIT-0

#!/bin/sh

# Assign an IP address to local loopback 
ip addr add 127.0.0.1/32 dev lo

ip link set dev lo up

# Add a hosts record, pointing target site calls to local loopback
echo "127.0.0.1   ip-ranges.amazonaws.com" >> /etc/hosts

touch /app/libnsm.so

# Run traffic forwarder in background and start the server
python3 /app/traffic_forwarder.py 127.0.0.1 443 3 8001 &
python3 /app/server.py server 5005
