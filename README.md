# Gnome-info-collect

*Gnome-info-collect* is a simple client-server application used for collecting system information on GNOME systems. The data will be used to improve GNOME, specifically by informing design decisions, influencing where resources are invested and generally help understand users better.

Initially, there was an online survey to be conducted, but it quickly became long and challenging to fill, while most of the questions were focusing on some setting of the user’s system. It is easier and **much more reliable** to collect the data using a tool than to depend on the user’s (often inaccurate) responses. Therefore, *gnome-info-collect* was made.

# Installation instructions

There are three possible ways to install *gnome-info-collect*:
1. using your distribution's package manager (fastest)
2. manual install using an installation package (rpm)
3. manually run from source

## Install using package manager

### Fedora, RHEL, CentOS

An up-to-date release is per convenience in a 
[Fedora Copr repo](https://copr.fedorainfracloud.org/coprs/vstanek/gnome-info-collect/ 
"Fedora Copr - vstanek/gnome-info-collect"). There are instalation instructions for both dnf/yum distros and for systems without dnf/yum (Silverblue/Kinoite).

### Other distributions

Currently looking for packagers to create their distribution package for *gnome-info-collect*.
After doing so, please, submit a merge request with installation instructions.

## Manual install using installation package (rpm)

There is always an up-to-date rpm package of *gnome-info-collect* in the 
[Releases page](https://gitlab.gnome.org/vstanek/gnome-info-collect/-/releases "gnome-info-collect releases"). Download it and use it for manual install. Follow your distribution instructions for installing the rpm.

## Manual run from source

There is also an up-to-date tarball of *gnome-info-collect* in the 
[Releases page](https://gitlab.gnome.org/vstanek/gnome-info-collect/-/releases "gnome-info-collect releases"), which you can use for running from source. 

The tarball contains a client application written in Python. Therefore, you need Python 3 (3.6 or newer) installed on your system. In addition to libraries contained in a standart python installation, it requires the `requests` package, which you can install by running `python -m pip install requests` in your terminal.

Then, simply run the app by running `python client.py` in your terminal.

# How it works

## Client & collected information

The client can be run on any GNOME system, where it collects the following data:

- Operating system 
  - distribution
  - variant
  - version
- Hardware
  - manufacturer/vendor
  - model
- Flatpak setup
  - installed/not installed
  - flathub status (enabled/filtered/disabled)
- Installed applications
- Favourited applications (the ones in dash)
- Types of GNOME online accounts setup
- Sharing settings enabled
  - file sharing (DAV)
  - remote desktop (VNC)
  - multimedia sharing
  - remote login (SSH)
- Workspaces settings
  - primary/all displays
  - dynamic/static
- Number of user on the system
- Default browser
- Enabled GNOME extensions
- [Salted hash](https://en.wikipedia.org/wiki/Salt_(cryptography) "Wikipedia - Salt (crptography)") of machine ID+username for de-doubling purposes

After the collection, the data is presented to the user for both confirmation and legal consent and then securely sent to a server for processing.

There is a check to prevent users running *gnome-info-collect* multiple times. If you try to send the data
again, after a successful previous attempt, no collection takes place and an info message is 
displayed instead.

## Server side

The server lives on GNOME OpenShift, recently migrated to version 4. When data is recieved, it is
validated to prevent junk from clogging the server. Then it is checked whether the specific data 
was not already recieved to prevent users from sending it multiple times. 
If the data is valid and was not previously submitted, it is saved for follow-up processing.

## Data security

The collected data is completely anonymous and will be used only for the purpose of enhancing usability 
and user experience of GNOME. Some of the steps to ensure anonymity include not collecting any personal 
information, such as username or email address, only system settings and some hardware properties. 
Additionally, some not needed data are deliberately discarded, such as the IP address of the sender and 
precise time of receiving the data.

As mentioned, to prevent double-sending, the client collects a 
[Salted hash](https://en.wikipedia.org/wiki/Salt_(cryptography) "Wikipedia - Salt (crptography)") of 
machine ID+username. It is **not possible** to get any information by receiving the hash code. All of this 
ensures that the data is confidential and untraceable.
