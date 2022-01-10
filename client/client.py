#!/usr/bin/env python

#  PROJECT: gnome-info-collect
#  FILE:    client/client.py
#  LICENCE: GPLv3+
#
#  Copyright 2022 vstanek <vstanek@redhat.com>

import subprocess
import requests
import os
import json

from gi.repository import GLib

# ~ User application data directory and status file
USER_DIR = GLib.get_user_data_dir()
APP_DIR = USER_DIR + '/gnome-info-collect'
STATUS_FILE = APP_DIR + '/uploaded'


def create_status_file():
    """Create a status file in user app dir

    To prevent user from uploading the data multiple times, create
    a status file in user's app dir. Created file is checked by
    check_already_uploaded().
    """

    if not os.path.isdir(APP_DIR):  # create app dir if doesn't exist
        os.mkdir(APP_DIR)
    with open(STATUS_FILE, 'x') as f:
        f.write('{"status": "successful"}\n')


def check_already_uploaded():
    """Check if status file exists (data already successfully uploaded)"""

    if os.path.isfile(STATUS_FILE):
        print("Information was already successfuly uploaded.")
        print("Not collecting or sending any data, exiting...")
        exit(0)


def collect_data() -> dict:
    # ~ Run the script and get the info
    try:
        json_output = subprocess.run(os.path.dirname(os.path.abspath(__file__)) + "/gnome-info-collect.sh", shell=False, capture_output=True, check=True).stdout
        return json_output
    except subprocess.CalledProcessError as e:
        print(f"Error collecting data!\nExit code: {e.returncode}\nOuptut: {e.output}")
        raise


def present_collected_data(data: dict):
    """ Present collected data to user

    @param data: dictionary (json) with data
    """

    # ~ Max length of a key in 'data' for pretty formatted output
    MAX_LEN = 26  # "Workspaces only on primary"

    print("The following information will be sent to the GNOME project:\n")
    for key, value in data.items():
        if key in ('Installed apps', 'Favourited apps',
                   'Online accounts', 'Enabled extensions'):
            # Value is an array
            print(f"**{key}**")
            if value == '"Error"':  # Error collecting this specific data
                print(f"Error collecting {key}")
            if not value:  # Empty array
                print("None")
            else:
                # unpack the array and print ' around
                print(*("'{}'".format(v) for v in value), sep=", ")
        else:
            print(f"**{key}**{(MAX_LEN-len(key)+4)*' '}{value}")

    print("\nThis information will be collected anonymously and will be used" +
          "to help improve the GNOME project.\n")


def get_permission() -> bool:
    """ Get user permission to upload collected data

    @return bool: True if permission granted, else False
    """

    try:
        print("Upload information? [y/N]: ", end="")
        c = input().strip()

        while c not in ('n', 'N', '', 'y', 'Y'):
            print("Invalid input, please try again.")
            print("Upload information? [y/N]: ", end="")
            c = input().strip()

        if c in ('n', 'N', ''):
            return False

        return True
    except KeyboardInterrupt:
        print("\nInterrupt registered, exiting...")  # Ctrl + C
        return False
    except EOFError:
        print("\nEOFError: EOF when reading input, exiting...")  # Ctrl + D
        return False


def upload_data(address: str, data: dict) -> bool:
    """Upload collected data to address via HTTP post request

    @param address: HTTP address of recieving server
    @param data: json data to send
    @return: False if error occured, True if successful
    """

    try:
        print("Uploading...")

        # ~ Send the data
        r = requests.post(address, data=json.dumps(data))

        # ~ Raise HTTPError if request returned an unsuccessful status code
        r.raise_for_status()

    except requests.HTTPError:
        print(f"Status {r.status_code}: An HTTP error occured.")
        print(f"Server message: {r.text}")
        return False
    except requests.ConnectionError:
        print("Connection Error: Error connecting to the server.")
        print("Please check your internet connection and try again.\n")
        raise
    except requests.Timeout:
        print("Timeout error: Request timed out.")
        print("Please check your internet connection and try again.\n")
        return False
    except Exception:
        print("Unknown error: Sending data unsuccessful, please, try again.\n")
        raise
    else:
        # ~ No errors, print server output
        print(f"Status {r.status_code}: {r.text}")
        # ~ Prevent user from double-sending
        create_status_file()
        return True


def main():
    # ~ Address of a server to send the data to
    ADDRESS = "https://gnome-info-collect-gnome-info-collect.openshift.gnome.org"

    check_already_uploaded()

    output = collect_data()
    # ~ Validate the data and convert to dict-like format for better processing
    try:
        data = json.loads(output)
    except ValueError:
        print("Error loading json data: invalid format.")
        raise

    present_collected_data(data)

    if not get_permission():
        print("Exiting...")
        return

    if upload_data(ADDRESS, data):
        # ~ Data successfully uploaded, finish
        print("Complete! Thank you for helping to improve GNOME.")


if __name__ == "__main__":
    main()
