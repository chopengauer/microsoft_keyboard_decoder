#!/usr/bin/python -u
# -*- coding: utf-8 -*-

import sys, os
import threading
import time
import subprocess
from usbhid import HIDKeyboard

class FifoReader(threading.Thread):
    def __init__(self, address = '2f9acf39a8', keystream = 'cd79d67ca9'):
        self.address = address
        self.keystream = keystream.decode('hex')
        self.process = subprocess.Popen(['./gfsk_finder %s' % self.address], stdout=subprocess.PIPE, shell = True)
        
        super(FifoReader, self).__init__()
        self._is_running = True
        self.seq = 0

    def run(self):
        pattern = '<find_address> Packet = %s' % self.address
        while (self._is_running):
            data = self.process.stdout.readline()
            if pattern in data:
                #print data
                index = data.find(pattern)
                hex_data = data[index+len(pattern):index+len(pattern)+40]
                #print hex_data
            try:
                self.decode(hex_data[1:31])
            except:
                pass

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

    def stop(self):
        print 'Stopping thread'
        self._is_running = False

if __name__ == "__main__":
    fiforeader = FifoReader(address='2f9acf39a8', keystream = 'cd79d67ca9')
    fiforeader.daemon = True
    fiforeader.start()
    while True:
        try:
            time.sleep(0.1)
        except KeyboardInterrupt:
            fiforeader.stop()
            sys.exit(0)
