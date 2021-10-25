#!/usr/bin/env python

#  PROJECT: gnome-info-collect
#  FILE:    client/client.py
#  LICENCE: GPLv3+
#  
#  Copyright 2021 vstanek <vstanek@redhat.com>

import subprocess
import requests
import os
from sys import stderr

# ~ Adress of a server to send the data to
ADDRESS="http://gnome-info-collect-gnome-info-collect.openshift.gnome.org"

# ~ Run the script and get the info
json_output = subprocess.run(os.path.dirname(__file__) + "/gnome-info-collect.sh", capture_output=True).stdout.decode()

# ~ Debug 
# stderr.write(f"Output:\n{json_output}\n")

try:
    # ~ Send the data
    r = requests.post(ADDRESS, data=json_output)
    # ~ Print server output
    print(f"{r.status_code}: {r.text}")
    
    if(r.status_code != 200): raise(Exception)
except:
    print("Sending data unsuccessful, please, try again.\n")
