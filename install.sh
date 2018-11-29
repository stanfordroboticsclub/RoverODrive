#!/usr/bin/env sh

yes | sudo pip3 install odrive

FOLDER=$(dirname $(realpath "$0"))

sudo ln -s $FOLDER/odrive.service /lib/systemd/system/
