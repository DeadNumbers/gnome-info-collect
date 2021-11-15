//  PROJECT: gnome-info-collect
//  FILE:    client/get_installed_apps.js
//  LICENCE: GPLv3+
//
//  Copyright 2021 vstanek <vstanek@redhat.com>
//
//  Code in this file gracefully provided by the awesome fmuellner <fmuellner@redhat.com>


const { Gio, GLib } = imports.gi;

const HAVE_MALCONTENT = imports.package.checkSymbol(
    'Malcontent', '0', 'ManagerGetValueFlags');
const Malcontent = HAVE_MALCONTENT
    ? imports.gi.Malcontent : null;

let appFilter;

if (HAVE_MALCONTENT) {
    const [, stdout] = GLib.spawn_command_line_sync('id -u');
    const uid = imports.byteArray.toString(stdout).trim();
    const manager = new Malcontent.Manager({
        connection:
            Gio.DBus.system
    });
    try {
        appFilter = manager.get_app_filter(
            uid,
            Malcontent.ManagerGetValueFlags.NONE,
            null);
    } catch (e) {
        logError(e);
    }
}

const apps = Gio.AppInfo.get_all().filter(app => {
    return app.should_show() &&
        (!appFilter || appFilter.is_appinfo_allowed(app));
});

if (apps.length === 0) { print('[]') }
else { print('["' + apps.map(app => app.get_id()).join('", "') + '"]') } //print as JSON array
