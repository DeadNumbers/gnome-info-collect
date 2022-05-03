# Gnome-info-collect

*Gnome-info-collect* is a simple client-server application used for collecting system information on GNOME systems. The data will be used to improve GNOME, specifically by informing design decisions, influencing where resources are invested and generally help understand users better.

Initially, there was an online survey to be conducted, but it quickly became long and challenging to fill, while most of the questions were focusing on some setting of the user’s system. It is easier and **much more reliable** to collect the data using a tool than to depend on the user’s (often inaccurate) responses. Therefore *gnome-info-collect* was made.

## Installation instructions

<!-- TODO -->

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
- [Salted hash](https://en.wikipedia.org/wiki/Salt_(cryptography)) of machine ID+username for de-doubling purposes

After the collection, the data is presented to the user for both confirmation and legal consent and then securely sent to a server for processing.

## Server side

The server lives on GNOME OpenShift, recently migrated to version 4.

<!-- TODO -->

## Data security

<!-- TODO -->
