#!/bin/sh

{
#~ Get list of all installed apps

gdbus call --session --dest org.gnome.Shell --object-path /org/gnome/Shell --method org.gnome.Shell.Eval 'imports.gi.Shell.AppSystem.get_default().get_installed().filter(app => imports.misc.parentalControlsManager.getDefault().shouldShowApp(app)).map(app => app.get_id())'


#~ Get list of GNOME favorited apps

favs=$(gsettings get org.gnome.shell favorite-apps); echo $favs | if grep -q "@as \[\]"; then echo None; else echo $favs; fi


#~ Get worspaces only on primary display

echo -n "Workspaces only on primary: "
gsettings get org.gnome.mutter workspaces-only-on-primary


#~ Get wheter workspaces are dynamic

echo -n "Workspaces dynamic: "
gsettings get org.gnome.shell.overrides dynamic-workspaces


#~ Get list of enabled GNOME extensions

gnome-extensions list --enabled

#~ Dump info into a file
} > info-dump.txt
