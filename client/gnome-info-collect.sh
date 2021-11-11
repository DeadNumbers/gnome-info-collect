#!/bin/sh

#  PROJECT: gnome-info-collect
#  FILE:    client/gnome-info-collect.sh
#  LICENCE: GPLv3+
#  
#  Copyright 2021 vstanek <vstanek@redhat.com>


{

#~ Start JSON object
echo "{"

#~ TODO: Sharing settings and online accounts, potentially GPU and graphic drivers
#~ ###############################################################################

#~ Enter client folder if not already there
cd $(dirname $(realpath $0))

#~ Get computer manufacturer, model and running operating system including its version
hostnamectl | grep -e 'Hardware' -e 'Operating System' | sed -e 's/^[ \t]*/"/g' -e 's/:[ \t]*/":"/g' -e 's/$/",/g' # Convert to JSON format using sed

#~ Check if flatpak is installed
flatpak 2>/dev/null
retval=$?
if [ $retval -eq 127 ]
    then 
        #~ Flatpak is not installed
        echo '"Flatpak installed":false,'
        echo '"Flathub enabled":false,'
    else
        #~ Flatpak is installed
        echo '"Flatpak installed":true,'
        
        #~ Check if flathub is enabled
        if flatpak remotes --columns url | grep 'https://dl.flathub.org/repo/' >/dev/null
            then
                echo '"Flathub enabled":true,'
            else
                echo '"Flathub enabled":false,'
        fi
fi

#~ Get list of all installed apps
installed_apps=$(gjs get_installed_apps.js 2>/dev/null || echo '"Error"')
echo "\"Installed apps\":$installed_apps,"

#~ Get list of favorited apps (in GNOME Dash)
favs=$(gsettings get org.gnome.shell favorite-apps || echo '"Error"')

echo -n '"Favourited apps":'
echo $favs | \
if grep -q "@as \[\]"
    then 
        echo '"None",' 
    else 
        echo "$favs," | sed -e "s/'/\"/g" -e "s/.desktop//g" # Substitute " for ' and remove .desktop
fi

#~ Get list of setup online accounts
accounts=$(gjs get_online_accounts.js 2>/dev/null || echo '"Error"')
echo "\"Online accounts\":$accounts,"

#~ Get sharing settings:
# File sharing (DAV)
echo -n "\"File sharing\":"
file_sharing=$(gsettings get org.gnome.settings-daemon.plugins.sharing.service:/org/gnome/settings-daemon/plugins/sharing/gnome-user-share-webdav/ enabled-connections || echo '"Error"')
echo $file_sharing | \
if grep -q "@as \[\]"
    then
        echo '"inactive",'
elif [ "$file_sharing" == '"Error"' ]
    then
        echo '"Error",'
    else
        echo '"active",'
fi
# Remote desktop (VNC)
echo -n "\"Remote desktop\":"
remote_desktop=$(gsettings get org.gnome.settings-daemon.plugins.sharing.service:/org/gnome/settings-daemon/plugins/sharing/gnome-remote-desktop/ enabled-connections || echo '"Error"')
echo $remote_desktop | \
if grep -q "@as \[\]"
    then
        echo '"inactive",'
elif [ "$remote_desktop" == '"Error"' ]
    then
        echo '"Error",'
    else
        echo '"active",'
fi
# Multimedia sharing
echo -n "\"Multimedia sharing\":"
multimedia_sharing=$(gsettings get org.gnome.settings-daemon.plugins.sharing.service:/org/gnome/settings-daemon/plugins/sharing/rygel/ enabled-connections || echo '"Error"')
echo $multimedia_sharing | \
if grep -q "@as \[\]"
    then
        echo '"inactive",'
elif [ "$remote_desktop" == '"Error"' ]
    then
        echo '"Error",'
    else
        echo '"active",'
fi
#~ Remote login (over SSH)
remote_login=$(systemctl is-active sshd)
echo "\"Remote login\":\"$remote_login\","

#~ Get worspaces only on primary display
workspaces_primary=$(gsettings get org.gnome.mutter workspaces-only-on-primary || echo '"Error"')
echo "\"Workspaces only on primary\":$workspaces_primary,"

#~ Get wheter workspaces are dynamic
workspaces_dynamic=$(gsettings get org.gnome.shell.overrides dynamic-workspaces || echo '"Error"')
echo "\"Workspaces dynamic\":$workspaces_dynamic,"

#~ Get number of user accounts
# Get min and max uid of a user account to filter out non-user accounts
uid_min=$(grep "^UID_MIN" /etc/login.defs); uid_max=$(grep "^UID_MAX" /etc/login.defs)
# Get user accounts from /etc/passwd and count them
num_users=$(awk -F':' -v "min=${uid_min##UID_MIN}" -v "max=${uid_max##UID_MAX}" '{ if ( $3 >= min && $3 <= max ) print $0}' /etc/passwd | wc -l)
echo "\"Number of users\":$num_users,"

#~ Get default browser
echo "\"Default browser\":\"$(xdg-mime query default x-scheme-handler/http)\"," | sed 's/.desktop//'

#~ Get list of enabled GNOME extensions
extensions=$(gnome-extensions list --enabled | sed -e 's/^/"/g' -e 's/$/",/g')
echo "\"Enabled extensions\":[$extensions]" | sed 's/,]/]/' # Don't forget to add a comma after the array if more commands follow after this one!

#~ End JSON object
echo "}"

#~ Dump info into a file
} # > info-dump.json # 2>/dev/null
