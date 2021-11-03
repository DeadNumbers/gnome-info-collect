const { Gio, GLib } = imports.gi;

const HAVE_MALCONTENT = imports.package.checkSymbol(
    'Malcontent', '0', 'ManagerGetValueFlags');
const Malcontent = HAVE_MALCONTENT
    ? imports.gi.Malcontent : null;

let appFilter;

if (HAVE_MALCONTENT) {
    const [, stdout] = GLib.spawn_command_line_sync('id -u');
    const uid = imports.byteArray.toString(stdout).trim();
    const manager = new Malcontent.Manager({ connection:
Gio.DBus.system });
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
print(apps.map(app => app.get_id()));
