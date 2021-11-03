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
try:
    json_output = subprocess.run(os.path.dirname(os.path.abspath(__file__)) + "/gnome-info-collect.sh", shell=False, capture_output=True, check=True).stdout
except subprocess.CalledProcessError as e:
    print(f"Error collecting the data!\nExit code: {e.returncode}\nOuptut: {e.output}")
    exit(e.returncode)
except PermissionError:
    print(f"Error collecting data: permission denied.")
    exit(9)

# ~ Debug 
# ~ print(f"Output:\n{json_output}\n")

try:
    # ~ Send the data
    r = requests.post(ADDRESS, data=json_output)
    
    # ~ Raise HTTPError if request returned an unsuccessful status code
    r.raise_for_status()
    
except requests.HTTPError:
    print(f"Status {r.status_code}: An HTTP error occured\nServer message: {r.text}\n")
    exit(10)
except requests.ConnectionError:
    print("Connection Error: Please check your internet connection and try again\n")
    exit(11)
except requests.Timeout:
    print("Timeout error: Request timed out\nPlease check your internet connection and try again\n")
    exit(12)
except:
    print("Unknown error: Sending data unsuccessful, please, try again.\n")
    exit(13)

else:
    # ~ No errors, print server output
    print(f"Status {r.status_code}: {r.text}")
