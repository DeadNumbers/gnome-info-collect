#!/usr/bin/env python

#  PROJECT: gnome-info-collect
#  FILE:    client/client.py
#  LICENCE: GPLv3+
#
#  Copyright 2022 vstanek <vstanek@redhat.com>

import requests
import os
import subprocess
import re
import json
import pwd
import webbrowser
import hashlib

import gi

gi.require_version('Goa', '1.0')
from gi.repository import GLib, Gio, Goa

# Older GNOME (<41) compatibility
try:
    gi.require_version('Malcontent', '0')
    from gi.repository import Malcontent
    HAVE_MALCONTENT = True
except (ValueError, ImportError):
    HAVE_MALCONTENT = False

# ~ User application data directory and status file
USER_DIR = GLib.get_user_data_dir()
APP_DIR = USER_DIR + '/gnome-info-collect'
STATUS_FILE = APP_DIR + '/uploaded'


class GCollector():
    """Class housing methods for collecting information for the
    gnome-info-collect project.
    """

    def __init__(self):
        self.data = dict()

    def collect_data(self) -> dict:
        """Collects data and returns it in a dictionary"""

        self._get_hw_os_info()
        self._get_flatpak_info()
        self._get_installed_apps()
        self._get_favourited_apps()
        self._get_online_accounts()
        self._get_sharing_settings()
        self._get_workspaces_status()
        self._get_number_of_users()
        self._get_default_browser()
        self._get_enabled_extensions()
        self._get_salted_machine_id_hash()

        return self.data

    def _get_hw_os_info(self):
        # hostnamectl --json=pretty doesn't work on older systems
        hw_os_info = subprocess.run(
            "hostnamectl",
            shell=False, capture_output=True, check=True
        ).stdout.decode()

        for i in ("Operating System", "Hardware Vendor", "Hardware Model"):
            try:
                res = re.search(f"{i}: (.*)$", hw_os_info, re.MULTILINE)
                if res is not None:
                    self.data[i.capitalize()] = res[1]
                else:
                    raise IndexError
            except IndexError:
                self.data[i.capitalize()] = "Error"

    def _get_flatpak_info(self):
        try:
            flatpak_retval = subprocess.run(
                "flatpak", shell=False, stderr=subprocess.DEVNULL
            ).returncode
            flatpak_installed = False if flatpak_retval == 127 else True

            if flatpak_installed:
                self.data["Flatpak installed"] = True

                # Flathub (enabled, filtered, disabled)
                flatpak_remotes = subprocess.run(
                    ["flatpak", "remotes", "--columns", "url,filter"],
                    shell=False, capture_output=True
                ).stdout.decode()
                flathub = re.search(
                    '(https://dl.flathub.org/repo/)\s*(\S*)',
                    flatpak_remotes)

                if flathub:
                    if flathub.group(2) == "-":
                        self.data["Flathub enabled"] = True
                    else:
                        self.data["Flathub enabled"] = "filtered"
                else:
                    self.data["Flathub enabled"] = False
            else:
                self.data["Flatpak installed"] = False
        except subprocess.CalledProcessError:
            raise

    def _get_installed_apps(self):
        if HAVE_MALCONTENT:
            stdout = GLib.spawn_command_line_sync('id -u')[1].decode()
            manager = Malcontent.Manager(
                connection=Gio.bus_get_sync(Gio.BusType.SYSTEM, None)
            )
            try:
                app_filter = manager.get_app_filter(
                    int(stdout),
                    Malcontent.ManagerGetValueFlags.NONE,
                    None
                )
            except Exception:
                raise
        else:
            app_filter = None

        apps = []
        for a in Gio.AppInfo.get_all():
            if a.should_show() and (not app_filter or app_filter.is_appinfo_allowed(a)):
                apps.append(re.sub(".desktop", "", a.get_id()))

        self.data["Installed apps"] = apps

    def _get_favourited_apps(self):
        favs = []
        for f in Gio.Settings(schema_id="org.gnome.shell").get_value("favorite-apps"):
            favs.append(str(re.sub(".desktop", "", f)))
        self.data["Favourited apps"] = favs

    def _get_online_accounts(self):
        goa_client = Goa.Client.new_sync(None)
        acc_objects = goa_client.get_accounts()

        accounts = []
        for acc in acc_objects:
            accounts.append(acc.get_account().props.provider_name)  # or provider_type

        self.data["Online accounts"] = accounts

    def _fetch_sharing_setting(self, service: str) -> bool:
        schema = "org.gnome.settings-daemon.plugins.sharing.service"
        path_base = "/org/gnome/settings-daemon/plugins/sharing/"

        setting = Gio.Settings.new_with_path(
            schema,
            path_base + service + "/"
        ).get_value("enabled-connections")
        return False if str(setting) == "@as []" else True

    def _get_sharing_settings(self):
        # File sharing (DAV)
        if self._fetch_sharing_setting("gnome-user-share-webdav"):
            self.data["File sharing"] = "active"
        else:
            self.data["File sharing"] = "inactive"

        # Remote desktop (VNC)
        # Need to check both gnome-remote-desktop and vino-server
        grd_on = self._fetch_sharing_setting("gnome-remote-desktop")
        vino_on = self._fetch_sharing_setting("vino-server")
        if (grd_on or vino_on):
            self.data["Remote desktop"] = "active"
        else:
            self.data["Remote desktop"] = "inactive"

        # Multimedia sharing
        if self._fetch_sharing_setting("rygel"):
            self.data["Multimedia sharing"] = "active"
        else:
            self.data["Multimedia sharing"] = "inactive"

        # Remote login (SSH)
        try:
            sshd_status = subprocess.run(
                ["systemctl", "is-active", "sshd"],
                shell=False, capture_output=True
            ).stdout.decode().strip()
            self.data["Remote login"] = sshd_status
        except subprocess.CalledProcessError:
            raise

    def _get_workspaces_status(self):
        mutter_settings = Gio.Settings(schema_id="org.gnome.mutter")

        # Workspaces only on primary display
        workspaces_primary = mutter_settings.get_value(
            "workspaces-only-on-primary"
        )
        self.data["Workspaces only on primary"] = bool(workspaces_primary)

        # Dynamic workspaces
        workspaces_dynamic = mutter_settings.get_value(
            "dynamic-workspaces"
        )
        self.data["Workspaces dynamic"] = bool(workspaces_dynamic)

    def _get_number_of_users(self):
        count = 0
        uid_min, uid_max = None, None

        if os.path.exists('/etc/login.defs'):
            with open("/etc/login.defs") as f:
                content = f.readlines()
            for line in content:
                if line.startswith('UID_MIN'):
                    uid_min = int(line.split()[1].strip())

                if line.startswith('UID_MAX'):
                    uid_max = int(line.split()[1].strip())
        else:
            uid_min = 1000
            uid_max = 60000

        for user in pwd.getpwall():
            if user.pw_uid >= uid_min and user.pw_uid <= uid_max:
                count += 1

        self.data["Number of users"] = count

    def _get_default_browser(self):
        self.data["Default browser"] = webbrowser.get().name

    def _get_enabled_extensions(self):
        enabled_extensions_list = []
        enabled_ext_setting = Gio.Settings(
            schema_id="org.gnome.shell"
        ).get_value("enabled-extensions")

        for ext in enabled_ext_setting:
            enabled_extensions_list.append(str(ext))

        self.data["Enabled extensions"] = enabled_extensions_list

    def _get_salted_machine_id_hash(self):
        hash = ""
        with open("/etc/machine-id") as f:
            hash = hashlib.sha256(
                ("gnome-info-collect" + f.read() + os.getlogin()).encode()
            ).hexdigest()
        self.data["Unique ID"] = hash


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

    print("\nThis information will be collected anonymously and will be used",
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

    output = GCollector().collect_data()
    # ~ Validate the data and convert to dict-like format for better processing
    try:
        json.dumps(output)
    except ValueError:
        print("Error loading json data: invalid format.")
        raise

    present_collected_data(output)

    if not get_permission():
        print("Exiting...")
        return

    if upload_data(ADDRESS, output):
        # ~ Data successfully uploaded, finish
        print("Complete! Thank you for helping to improve GNOME.")


if __name__ == "__main__":
    main()
