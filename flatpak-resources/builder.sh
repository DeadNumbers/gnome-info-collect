#!/bin/bash

python flatpak-pip-generator --requirements-file=pip-requirements.txt --output python-dependencies

sudo flatpak-builder --force-clean ./build org.gnome.gnome-info-collect.yml