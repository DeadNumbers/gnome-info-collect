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

from gi.repository import GLib

# ~ Address of a server to send the data to
ADDRESS = "https://gnome-info-collect-gnome-info-collect.openshift.gnome.org"
# ~ Max length of a key in json for pretty formatted output
MAX_LEN = 26 # "Workspaces only on primary"
# ~ User application data directory and status file
USER_DIR = GLib.get_user_data_dir()
APP_DIR = USER_DIR + '/gnome-info-collect'
STATUS_FILE = APP_DIR + '/uploaded'


# ~ Check if status file exists (if data was already once successfully uploaded) and exit if yes
if os.path.isfile(STATUS_FILE):
    print("Information was already successfuly uploaded.\nNot collecting or sending any data, exiting...")
    exit(0)

# ~ Run the script and get the info
try:
    json_output = subprocess.run(os.path.dirname(os.path.abspath(__file__)) + "/gnome-info-collect.sh", shell=False, capture_output=True, check=True).stdout
except subprocess.CalledProcessError as e:
    print(f"Error collecting data!\nExit code: {e.returncode}\nOuptut: {e.output}")
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
        if value == '"Error"': # Error collecting this specific data
            print(f"Error collecting {key}")
        if not value: # Empty array
            print("None")
        else:
            print(*("'{}'".format(v) for v in value), sep=", ") # unpack the array and print ' around
    else:
        print(f"**{key}**{(MAX_LEN-len(key)+4)*' '}{value}")

print("\nThis information will be collected anonymously and will be used to help improve the GNOME project.\n")

# ~ Ask user for permission
print("Upload information? [y/N]: ", end="")
try:
    c = input()

    if c in ('n', 'N', ''):
        print("Exiting...")
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

# ~ No errors, print server output
print(f"Status {r.status_code}: {r.text}")

# ~ Create a file in user app dir to preven user from uploading the data multiple times
if not os.path.isdir(APP_DIR): # create app dir if doesn't exist
    os.mkdir(APP_DIR)
with open(STATUS_FILE, 'x') as f:
    f.write('{"status": "successful"}\n')

# ~ Finish
print("Complete! Thank you for helping to improve GNOME.")
