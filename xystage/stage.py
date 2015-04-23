import numpy as np

import serial
import time


class Stage(object):
    def __init__(self, port = 'COM6'):
        self.s = serial.Serial()
        self.s.setPort(port)
        self.s.setDTR(False)
        self.s.timeout = 0
        self.s.open()
    def sendget(self,cmdstr,timeout=2):
        self.s.readlines()
        self.s.write(cmdstr)
        tic = time.time()
        resp = ''
        while time.time()-tic < timeout:
            resp += self.s.read()
            if '>' in resp:
                break
        return resp