#!/usr/bin/env python

from omxplayer.player import OMXPlayer
import subprocess
import logging
import sys
from time import sleep


class Player:
    def __init__(self):
        self.image_url = ""
        self.site_url = ""
        self.player = None
        self.fbi = None

    def set_image_url(self, url):
        self.image_url = url.replace('file://', '')
        subprocess.Popen(['/usr/bin/sudo', 'killall', '-q', 'fbi'])
        sleep(1)
        subprocess.Popen(['/usr/bin/sudo', '/usr/bin/fbi', '-noverbose', '-a', '-T', '1', self.image_url])

    def set_site_url(self, url):
        self.site_url = url

    def start(self):
        self.player = OMXPlayer(
            self.site_url,
            dbus_name='org.mpris.MediaPlayer2.omxplayer1',
            args=['--no-osd', '-o', 'hdmi', '-b']
        )

    def resume(self):
        self.player.show_video()
        self.player.play()
    
    def pause(self):
        self.player.pause()
        self.player.hide_video()

    def stop(self):
        if self.player:
            self.player.quit()

if __name__ == '__main__':
    from time import sleep

    # test
    omxplayer = Player()
    omxplayer.set_image_url("file:///home/pi/bcontrol/media/test_image.png")
    omxplayer.set_site_url("file:///home/pi/bcontrol/media/test_video.mp4")

    omxplayer.start()
    sleep(10)
    omxplayer.pause()
    sleep(5)
    omxplayer.resume()
    sleep(5)
    omxplayer.stop()

    sleep(5)

    omxplayer.set_site_url("file:///home/user/pi/bcontrol/media/test_video.mp4")
    omxplayer.start()
    sleep(10)
    omxplayer.stop()
