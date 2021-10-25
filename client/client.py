#!/usr/bin/env python

#  PROJECT: gnome-info-collect
#  FILE:    client/client.py
#  LICENCE: GPLv3+
#  
#  Copyright 2021 vstanek <vstanek@redhat.com>

import subprocess
import requests
import os

# ~ Address of a server to send the data to
ADDRESS="https://gnome-info-collect-gnome-info-collect.openshift.gnome.org"

# ~ Run the script and get the info
json_output = subprocess.run(os.path.dirname(__file__) + "/gnome-info-collect.sh", capture_output=True).stdout.decode()

# ~ Debug 
# print(f"Output:\n{json_output}\n")

try:
    # ~ Send the data
    r = requests.post(ADDRESS, data=json_output)
    
    # ~ Raise HTTPError if request returned an unsuccessful status code
    r.raise_for_status()
    
except requests.HTTPError:
    print(f"Status {r.status_code}: An HTTP error occured\n")
except requests.ConnectionError:
    print("Connection Error: please check your internet connection and try again\n")
except requests.Timeout:
    print("Timeout error: request timed out\nPlease check your internet connection and try again\n")
except:
    print("Unknown error: sending data unsuccessful, please, try again.\n")

else:
    # ~ No errors, print server output
    print(f"Status {r.status_code}: {r.text}")
    
