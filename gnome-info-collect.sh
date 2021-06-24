#!/bin/sh

{

#~ Start JSON object
echo "{"
    
#~ Get computer manufacturer, model and running operating system 
#~ including its version

hostnamectl | grep -e 'Hardware' -e 'Operating System' | sed -e 's/^[ \t]*/"/g' -e 's/:[ \t]*/":"/g' -e 's/$/",/g' #Convert to JSON format using sed

#~ Get list of all installed apps

installed_apps=$(gdbus call --session --dest org.gnome.Shell --object-path /org/gnome/Shell --method org.gnome.Shell.Eval 'imports.gi.Shell.AppSystem.get_default().get_installed().filter(app => imports.misc.parentalControlsManager.getDefault().shouldShowApp(app)).map(app => app.get_id())' || echo '"Error"')

echo -n '"Installed apps":'
if [ "$installed_apps" != '"Error",' ]
    then
        echo $installed_apps | grep -o '\[.*]' | sed -e 's/.desktop//g' -e 's/]/],/'
    else
        echo $installed_apps
fi

#~ Get list of favorited apps (in Dash)

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

#~ Get list of enabled GNOME extensions

extensions=$(gnome-extensions list --enabled | sed -e 's/^/"/g' -e 's/$/",/g')
echo "\"Enabled extensions\":[$extensions]" | sed 's/,]/]/' #Don't forget to add a comma after the array if more commands follow after this one!

#~ End JSON object
echo "}"

#~ Dump info into a file
} > info-dump.json # 2>/dev/null
