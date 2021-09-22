#!/bin/sh

{

#~ Start JSON object
echo "{"
    
#~ Get computer manufacturer, model and running operating system 
#~ including its version
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
installed_apps=$(gdbus call --session --dest org.gnome.Shell --object-path /org/gnome/Shell --method org.gnome.Shell.Eval 'imports.gi.Shell.AppSystem.get_default().get_installed().filter(app => imports.misc.parentalControlsManager.getDefault().shouldShowApp(app)).map(app => app.get_id())' || echo '"Error"')

echo -n '"Installed apps":'
if [ "$installed_apps" != '"Error",' ]
    then
        echo $installed_apps | grep -o '\[.*]' | sed -e 's/.desktop//g' -e 's/]/],/'
    else
        echo $installed_apps
fi

#~ Get list of favorited apps (in GNOME Dash)
favs=$(gsettings get org.gnome.shell favorite-apps || echo '"Error",')

echo -n '"Favourited apps":'
echo $favs | \
if grep -q "@as \[\]"
    then 
        echo '"None"' 
    else 
        echo "$favs," | sed -e "s/'/\"/g" -e "s/.desktop//g" # Substitute " for ' and remove .desktop
fi


#~ Get worspaces only on primary display
workspaces_primary=$(gsettings get org.gnome.mutter workspaces-only-on-primary || echo '"Error",')
echo "\"Workspaces only on primary\":$workspaces_primary,"

#~ Get wheter workspaces are dynamic
workspaces_dynamic=$(gsettings get org.gnome.shell.overrides dynamic-workspaces || echo '"Error",')
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
} > info-dump.json # 2>/dev/null
