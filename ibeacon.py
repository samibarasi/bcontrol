#!/usr/bin/env python

from beacontools import BeaconScanner, IBeaconFilter
import math
import numpy as np
from numpy_ringbuffer import RingBuffer
from time import sleep, time
import json
import sys
import logging

class IBeacon:

    def __init__(self, config, ret):
        self.config = config
        self.ret = ret
        self.ibeacons = {}
        self.ibeacons_inrange = 0
        self.running = True

        self.scanner = BeaconScanner(self.callback)

        self.scanner.start()

    def set_config(self, config):
        self.config = config

    def distance(self, txPower, rssi):
        ratio_db = txPower - rssi
        ratio_linear = math.pow(10.0, ratio_db / 10.0)
        return math.sqrt(ratio_linear)

    def callback(self, bt_addr, rssi, packet, additional_info):
        #print("<%s, %d> %s %s" % (bt_addr, rssi, packet, additional_info))
        if not hasattr(packet, 'uuid'):
            return
        uuid = packet.uuid
        if uuid not in self.config['uuids']:
            if self.distance(packet.tx_power, rssi) < self.config['startrange']:
                self.ret("unknown:%s" % uuid)
                if uuid in self.ibeacons:
                    if self.ibeacons[uuid]['inrange']:
                        self.ibeacons_inrange -= 1
                    del self.ibeacons[uuid]
            return

        if uuid not in self.ibeacons:
            self.ibeacons[uuid] = {
                'current_distance': 99,
                'count': 0,
                'inrange': False,
                'reset': False,
                'buffer': RingBuffer(capacity=10, dtype=np.float),
                'last': time()
            }

        self.ibeacons[uuid]['buffer'].append(self.distance(packet.tx_power, rssi))
        self.ibeacons[uuid]['current_distance'] = np.percentile(np.array(self.ibeacons[uuid]['buffer']), 50) * 10000

        now = time()
        if now - self.ibeacons[uuid]['last'] > 1:

            logging.debug("%s - %d - %d(%d)" % (
                uuid, int(self.ibeacons[uuid]['current_distance']), self.ibeacons_inrange, self.config['inrange']))

            self.ibeacons[uuid]['last'] = now

            if self.ibeacons[uuid]['inrange']:
                if self.ibeacons[uuid]['current_distance'] > float(self.config['stoprange']):
                    self.ibeacons[uuid]['inrange'] = False
                    self.ibeacons_inrange -= 1

                    logging.debug(uuid + ": out of range")
                    if self.ibeacons_inrange < self.config['inrange'] and self.ibeacons_inrange + 1 >= self.config['inrange']:
                        logging.debug("not enough ibeacons in range")
                        self.ibeacons[uuid]['reset'] = True
                        self.ret("pause")
                else:
                    self.ibeacons[uuid]['count'] = 0
            else:
                if self.ibeacons[uuid]['current_distance'] < float(self.config['startrange']):
                    self.ibeacons[uuid]['inrange'] = True
                    self.ibeacons_inrange += 1
                    logging.debug(uuid + ": in range")
                    if self.ibeacons_inrange == self.config['inrange']:
                        logging.debug("enough ibeacons in range")
                        if self.ibeacons[uuid]['reset']:
                            self.ret("resume")
                        else:
                            self.ret("start")
                else:
                    self.ibeacons[uuid]['count'] += 1
                    if self.ibeacons[uuid]['reset'] and self.ibeacons[uuid]['count'] > int(self.config['timeout']):
                        if self.ibeacons_inrange < self.config['inrange']:
                            logging.debug("not enough ibeacons in range -> reset")
                            self.ret("stop")
                        self.ibeacons[uuid]['reset'] = False

    def run(self):
        try:
            while self.running:
                sleep(10)
        except KeyboardInterrupt:
            print "bye"

        self.terminate()

    def terminate(self):
        self.scanner.stop()

def test_callback(msg):
    print "callback: " + str(msg)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", help="Configuration", default="config.json")
    args = parser.parse_args()
    config = {}
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
    with open(args.config, 'r') as stream:
        try:
            config = json.load(stream)
        except Exception, e:
            logging.error("can't read configuration: %s", e)
            sys.exit(1)

    ibeacon = IBeacon(config, test_callback)

    ibeacon.run()
