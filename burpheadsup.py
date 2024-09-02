#!/usr/bin/python3

import http.client
import sys
import random
import json
from os import system

HOST = "localhost"
PORT = 47674
SIGNAL_NB = 12

STATUSES = {
    "intercept": "🔴 INTERCEPT",
    "pass": "🟢 PASS",
    "off": "⚫️ OFF"
}

# This will be called from i3blocks/the GUI that needs the output
if "--get-status" in sys.argv:

    def print_status(status):
        if status in STATUSES.keys():
            print(f"{STATUSES[status]:11}")
        else:
            print("[burpheadsup] error: received unexpected response")
            # print(status)


    connection = http.client.HTTPConnection(HOST, PORT)

    try:
        connection.request("GET", "/intercept/status")
        response = connection.getresponse()
        print_status(json.loads(response.read()).get('status'))
    except (ConnectionRefusedError, json.JSONDecodeError):
        print_status("off")


# This will be called from the keyboard shortcut to toggle the proxy
elif "--toggle" in sys.argv:

    connection = http.client.HTTPConnection(HOST, PORT)
    try:
        connection.request("GET", "/intercept/toggle")
    except ConnectionRefusedError:
        # still need to notify i3blocks
        pass

    # notify i3blocks
    system(f"pkill -SIGRTMIN+{int(SIGNAL_NB)} i3blocks")

else:
    print("Missing arguments --toggle or --get-status")
