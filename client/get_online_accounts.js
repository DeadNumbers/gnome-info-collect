//  PROJECT: gnome-info-collect
//  FILE:    client/get_online_accounts.js
//  LICENCE: GPLv3+
//
//  Copyright 2021 vstanek <vstanek@redhat.com>


const Goa = imports.gi.Goa;

const goaClient = Goa.Client.new_sync(null);


let accountObjects;
try {
    accountObjects = goaClient.get_accounts();
} catch(e) {
    logError(e);
}


const accounts = accountObjects.map(acc => acc.get_account().providerName); //providerType also available

print('["' + accounts.join('", "') + '"]'); //print as a JSON array
