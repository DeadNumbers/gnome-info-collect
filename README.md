# gnome-info-collect

*gnome-info-collect* is a simple client-server application used for collecting information on GNOME systems. The data will be used to improve GNOME, specifically by informing design decisions, influencing where resources are invested, and generally helping us to understand users better.

Help is wanted with packaging and the installation instructions - please create merge requests if there are mistakes or omissions!

## How to install

Packages are available for the following distributions. If a package isn't available for your distro, see below for manual installation options.

### Fedora

The [Fedora Copr repo](https://copr.fedorainfracloud.org/coprs/vstanek/gnome-info-collect/ 
"Fedora Copr - vstanek/gnome-info-collect") is the recommended way to install gnome-info-collect on Fedora. To install, run:

```
sudo dnf copr enable vstanek/gnome-info-collect
sudo dnf install gnome-info-collect
```

### Arch

Install the [gnome-info-collect](https://archlinux.org/packages/gnome-info-collect) package by running:

```
sudo pacman -S gnome-info-collect
```

### openSUSE

Install the [gnome-info-collect](https://build.opensuse.org/package/show/GNOME:Next/gnome-info-collect) package by running:

```
zypper addrepo https://download.opensuse.org/repositories/GNOME:Next/openSUSE_Factory/GNOME:Next.repo
zypper refresh
zypper install gnome-info-collect
```

### Ubuntu

Install the [gnome-info-collect](https://snapcraft.io/gnome-info-collect) package by running:

```
sudo snap install --classic  gnome-info-collect
```

There is currently a known issue with using this snap on earlier versions of Ubuntu. If you are running Ubuntu 20 and earlier, follow the instructions for [manual installation](https://gitlab.gnome.org/vstanek/gnome-info-collect#manual-installation) at the bottom.

## How to run

Once gnome-info-collect is installed, just run `gnome-info-collect` from the Terminal.

## How it works

### Client & collected information

The client can be run on any GNOME system, where it collects the following data:

| Data             | Research Questions |
|------------------|--------------------|
| Distribution, variant, version | Who is providing data? Is the information influnced by the distribution used? |
| Hardware (manufacturer/vendor, model)             | Which hardware should GNOME prioritize its support for? |
| Flatpak installed?                                | To what extent should GNOME Software be designed around Flatpak being available? |
| Flathub status (enabled/filtered/disabled)        | To what extent should GNOME Software be designed around Flathub being available? |
| Installed applications                            | Which applications should GNOME prioritise the development of? Are there any 3rd party apps that could be moved to core? |
| Favourited applications (the ones in dash)        | Is the customizable dash a useful feature? Which apps should be favourited by default? |
| Types of GNOME online accounts setup              | Which accounts does GNOME need to continue supporting? To what extent is GOA used? |
| Sharing settings enabled (file sharing (DAV), remote desktop (VNC & RDP), multimedia sharing, remote login (SSH)) | Which sharing settings need to continue being part of the Settings app? Which could be moved elsewhere? |
| Workspaces on primary only/workspaces on all displays | What level of resources should be in invested in workspaces on all displays? |
| Dynamic/static workspaces                         | What level of resources should be invested in static workspaces? |
| Number of users on the system                     | Does the multiuser experience deserve more attention? |
| Default browser                                   | Where should browser integration work be focused? |
| Enabled GNOME extensions                          | Any changes from extensions that should be considered for the default shell experience? |
| [Salted hash](https://en.wikipedia.org/wiki/Salt_(cryptography) "Wikipedia - Salt (crptography)") of machine ID+username | Used to de-duplicate responses |

After the collection, the data is presented to the user for both confirmation and legal consent and then securely sent to a server for processing.

There is a check to prevent users running *gnome-info-collect* multiple times. If you try to send the data
again, after a successful previous attempt, no collection takes place and an info message is 
displayed instead.

### Server side

The server lives on GNOME OpenShift, recently migrated to version 4. When data is recieved, it is
validated to prevent junk from clogging the server. Then it is checked whether the specific data 
was not already recieved to prevent users from sending it multiple times. 
If the data is valid and was not previously submitted, it is saved for follow-up processing.

### Data security

The collected data is completely anonymous and will be used only for the purpose of enhancing the usability 
and user experience of GNOME. Some of the steps to ensure anonymity include not collecting any personal 
information, such as username or email address, only system settings and some hardware properties. 
Additionally, some not needed data are deliberately discarded, such as the IP address of the sender and 
precise time of receiving the data.

As mentioned, to prevent double-sending, the client collects a 
[salted hash](https://en.wikipedia.org/wiki/Salt_(cryptography) "Wikipedia - Salt (crptography)") of 
machine ID+username. It is **not possible** to get any information by receiving the hash code. All of this 
ensures that the data is confidential and untraceable.

## Manual installation

If a package isn't available for your distribution, the following options are available.

### Manually install an RPM

RPM packages of *gnome-info-collect* releases can be found in the 
[releases page](https://gitlab.gnome.org/vstanek/gnome-info-collect/-/releases "gnome-info-collect releases"). Follow your distribution instructions for installing the RPM.

### Manually run from source

Tarballs of *gnome-info-collect* releases can be found on the 
[releases page](https://gitlab.gnome.org/vstanek/gnome-info-collect/-/releases "gnome-info-collect releases"), which you can use for running from source. 

The tarball contains a client application written in Python. Therefore, you need Python 3 (3.7 or newer) installed on your system. In addition to libraries contained in a standard Python installation, it requires the `requests` package, which you can install by running `python -m pip install requests` in your terminal.

Then, simply run the app by running `python client.py` in your terminal.
