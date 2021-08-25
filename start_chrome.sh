#!/bin/bash

#sleep 10

export DISPLAY=:0.0

#killall socat
killall chrome

sleep 1

# start socat
#/usr/bin/socat tcp-listen:9222,fork tcp:localhost:9223 &

. ~/bcontrol/systemd.conf

# start chrome
rm -r ~/.config/google-chrome/Default/ && rm -r ~/.cache/google-chrome

sleep 1

/usr/bin/google-chrome-stable ${CHROME_START_PARAMS} &
