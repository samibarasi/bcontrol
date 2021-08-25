#!/usr/bin/python

from time import sleep
from beacontools import BeaconScanner, IBeaconFilter
import math
import numpy as np
from numpy_ringbuffer import RingBuffer
import argparse
import json
import logging
import pychrome
from subprocess import Popen

def distance(txPower, rssi):
    ratio_db = txPower - rssi
    ratio_linear = math.pow(10.0, ratio_db / 10.0)
    return math.sqrt(ratio_linear)
    
    #if (rssi == 0):
    #    return -1
    #ratio = rssi * 1.0 / txPower
    #if ratio < 1.0:
    #    return math.pow(ratio, 10)
    #else:
    #    return (0.89976) * math.pow(ratio, 7.7095) + 0.111

def read_config(file_name):
    with open(file_name, 'r') as stream:
        try:
            return json.load(stream)
        except yaml.YAMLError as exc:
            logging.error("can't read configuration")
            sys.exit(1)


def callback(bt_addr, rssi, packet, additional_info):
    global r, current_distance
    #print("<%s, %d> %s %s" % (bt_addr, rssi, packet, additional_info))
    r.append(distance(packet.tx_power, rssi))
    current_distance = np.percentile(np.array(r), 50)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", help="Configuration", default="config.json")
    parser.add_argument("-l", "--logfile", help="Logfile", default="ibeacon.log")
    args = parser.parse_args()

    # read configuration
    config = read_config(args.config)

    # start chrome
    Popen(["/usr/bin/google-chrome-stable", "--start-fullscreen", "--remote-debugging-port=9222", "--password-store=basic"])
    sleep(5)

    # connect to chrome
    browser = pychrome.Browser(url="http://127.0.0.1:9222")
    tabs = browser.list_tab()
    tab = tabs[0]
    tab2 = tabs[1]
    tab.start()
    tab2.start()
    tab.Page.navigate(url=config['image_url'])
    tab2.Page.navigate(url=config['url'])

    tab2.Network.enable()

    # logger
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s', filename=args.logfile, filemode='w')

    r = RingBuffer(capacity=10, dtype=np.float)
    current_distance = 99

    scanner = BeaconScanner(callback, 
        device_filter=IBeaconFilter(uuid=config['uuid'].lower())
    )
    scanner.start()

    show_site = False
    show_image = True

    count = 0
    inRange = True
    reset = False

    try:
        while True:
            sleep(1)

            print current_distance

            if inRange:
                if current_distance > float(config['stoprange']):
                    browser.activate_tab(tab)
                    inRange = False
                    print "out of range"
                    reset = True
                else:
                    count = 0
            else:
                if current_distance < float(config['startrange']):
                    browser.activate_tab(tab2)
                    inRange = True
                    print "in range"
                else:
                    count += 1
                    if reset and count > int(config['timeout']):
                        browser.activate_tab(tab)
                        tab2.Page.navigate(url=config['url'])
                        reset = False
                        print "reset"

    except KeyboardInterrupt:
        print("\nstop")

    scanner.stop()

