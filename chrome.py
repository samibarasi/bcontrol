#!/usr/bin/env python

import pychrome
import logging
import socket
import sys


class Chrome:
    def __init__(self, chrome_host, chrome_port):
        self.chrome_url = "http://%s:%s" % (
            socket.gethostbyname(chrome_host),
            chrome_port
        )

        self.browser = pychrome.Browser(url=self.chrome_url)


        tabs = self.browser.list_tab()
        if len(tabs) != 2:
            logging.error("start chrome browser with exactly 2 tabs in fullscreen/kiosk mode")
            sys.exit(1)

        self.image_tab = tabs[0]
        self.site_tab = tabs[1]

        self.image_tab.start()
        self.site_tab.start()

        self.image_url = ""
        self.site_url = ""

        # register callback if you want
        def request_will_be_sent(**kwargs):
            print("loading: %s" % kwargs.get('request').get('url'))

        #self.site_tab.Network.requestWillBeSent = request_will_be_sent

        self.site_tab.Network.enable()

        # initial enable image_tab
        self.browser.activate_tab(self.image_tab)

    def set_image_url(self, url):
        self.image_url = url
        self.image_tab.Page.navigate(url=url)

    def set_site_url(self, url):
        self.site_url = url
        self.site_tab.Storage.clearDataForOrigin(origin="file://", storageTypes="local_storage")
        self.site_tab.Page.navigate(url=url)

    def start(self):
        self.browser.activate_tab(self.site_tab)

    def resume(self):
        self.browser.activate_tab(self.site_tab)

    def pause(self):
        self.browser.activate_tab(self.image_tab)

    def stop(self):
        self.site_tab.Storage.clearDataForOrigin(origin="file://", storageTypes="local_storage")
        self.site_tab.Page.reload()
        self.browser.activate_tab(self.image_tab)

if __name__ == '__main__':
    from time import sleep

    # test
    chrome = Chrome("cube02.fritz.box", 9222)
    chrome.set_image_url("file:///home/user/wbt/test_image.png")
    chrome.set_site_url("file:///home/user/wbt/imat/story_html5.html")

    sleep(20)
    chrome.start()
    sleep(10)
    chrome.pause()
    sleep(10)
    chrome.resume()
    sleep(10)
    chrome.pause()
    sleep(10)
    chrome.resume()
    sleep(10)
    chrome.pause()
    sleep(10)
    chrome.stop()
    sleep(10)
    chrome.start()
    sleep(10)
    chrome.pause()
    sleep(10)
    chrome.resume()
