#!/usr/bin/env python

#  PROJECT: gnome-info-collect
#  FILE:    client/client.py
#  LICENCE: GPLv3+
#  
#  Copyright 2021 vstanek <vstanek@redhat.com>

import subprocess
import requests
import os
import json

# ~ Address of a server to send the data to
ADDRESS = "https://gnome-info-collect-gnome-info-collect.openshift.gnome.org"
# ~ Max length of a key in json for pretty formatted output
MAX_LEN = 26 # "Workspaces only on primary"

# ~ Run the script and get the info
try:
    json_output = subprocess.run(os.path.dirname(os.path.abspath(__file__)) + "/gnome-info-collect.sh", shell=False, capture_output=True, check=True).stdout
except subprocess.CalledProcessError as e:
    print(f"Error collecting the data!\nExit code: {e.returncode}\nOuptut: {e.output}")
    exit(e.returncode)
except PermissionError:
    print(f"Error collecting data: permission denied.")
    exit(8)

# ~ Debug 
# ~ print(f"Output:\n{json_output}\n")

# ~ Validate the data and convert to dict-like format for better processing
try:
    data = json.loads(json_output)
except ValueError:
    print("Error loading json data: invalid format.")
    exit(9)

# ~ Show data to user
print("The following information will be sent to the GNOME project:\n")
for key, value in data.items():
    if key in ('Installed apps', 'Favourited apps', 'Online accounts', 'Enabled extensions'): # Value is an array
        print(f"**{key}**")
        print(*("'{}'".format(v) for v in value), sep=", ") # unpack the array and print ' around
    else:
        print(f"**{key}**{(MAX_LEN-len(key)+4)*' '}{value}")

print("\nThis information will be collected anonymously and will be used to help improve the GNOME project.\n")

# ~ Ask user for permission
print("Upload information? [y/N]: ", end="")
try:
    c = input()

    if c in ('n', 'N', ''):
        exit(0)
    elif c not in ('y', 'Y'):
        raise ValueError
except KeyboardInterrupt:
    print("\nInterrupt registered, exiting...")
    exit(10)
except EOFError:
    print("\nEOFError: EOF when reading input, exiting...")
    exit(11)
except ValueError: # Not [nNyY] or ''
    print("Invalid input, exiting...")
    exit(12)

try:
    print("Uploading...")
    
    # ~ Send the data
    r = requests.post(ADDRESS, data=json_output)
    
    # ~ Raise HTTPError if request returned an unsuccessful status code
    r.raise_for_status()
    
except requests.HTTPError:
    print(f"Status {r.status_code}: An HTTP error occured\nServer message: {r.text}.")
    exit(20)
except requests.ConnectionError:
    print("Connection Error: Please check your internet connection and try again.\n")
    exit(21)
except requests.Timeout:
    print("Timeout error: Request timed out\nPlease check your internet connection and try again.\n")
    exit(22)
except:
    print("Unknown error: Sending data unsuccessful, please, try again.\n")
    exit(23)
else:
    # ~ No errors, print server output
    print(f"Status {r.status_code}: {r.text}")

print("Complete! Thank you for helping to improve GNOME.")
