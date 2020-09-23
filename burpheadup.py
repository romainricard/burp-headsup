#!/usr/bin/python3

import http.client
import sys
import random
from os import system

HOST = "localhost"
PORT = 8042
KEY = "3ce7a61896d5fe8729_DEFAULT_KEY_CHANGEME_287ad2ac2d7b9" # CHANGEME
SIGNAL_NB = 12

# Constants, no need to edit
INTERCEPT = "INTERCEPT"
PASS = "PASS"
WRONG_KEY = "ERR WRONG KEY"
OFF = "Off"

def get_status():
    try:
        with open("/tmp/.burpheadup_status", "r") as f_in:
            return f_in.read()
    except FileNotFoundError:
        return OFF

def write_status(status):
    with open("/tmp/.burpheadup_status", "w") as f_out:
        f_out.write(status)
        f_out.close()



# This will be called from i3blocks/the GUI that needs the output
if "--get-status" in sys.argv:

    status = get_status()

    if status == INTERCEPT:
        print("🔴 {:9}".format(INTERCEPT))
    elif status == PASS:
        print("🔵 {:9}".format(PASS))
    elif status == WRONG_KEY:
        print(WRONG_KEY)
    else:
        print(OFF)


# This will be called from the keyboard shortcut to toggle the proxy
elif "--toggle" in sys.argv:

    connection = http.client.HTTPConnection(HOST, PORT)
    try:
        connection.request("GET", "/proxy/toggle?key={}".format(KEY))
        response = connection.getresponse()
        
        if response.status == 403:
            print("Wrong key.")
            write_status(WRONG_KEY)
        else:
            reponse_text = response.read().decode()
            write_status(reponse_text if reponse_text in [INTERCEPT, PASS] else OFF)

    except ConnectionRefusedError:
        write_status(OFF)

    # notify i3blocks
    system("pkill -SIGRTMIN+{} i3blocks".format(int(SIGNAL_NB)))

else:
    print("Missing arguments --toggle or --get-status")