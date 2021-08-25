#!/bin/bash

. /etc/profile

sudo setcap 'cap_net_raw,cap_net_admin+eip' $(readlink -f $(which python))
cd /home/pi/bcontrol
. /home/pi/bcontrol/systemd.conf
./bcontrol.py ${BCONTROL_START_PARAMS}
