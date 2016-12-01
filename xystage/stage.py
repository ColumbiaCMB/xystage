import numpy as np

import serial
import time
import platform
if platform.system() == 'Windows':
    default_port = 'COM6'
else:
    default_port = '/dev/ttyACM1'

hwp_speed = 800,8000
hwp_acceleration = 2000
hwp_stepping = 16


class StatusBits(object):
    def __repr__(self):
        return "\n".join([('%s:%s' % (k,v)) for k,v in self.__dict__.items()])

class Stage(object):
    def __init__(self, port = default_port):
        #Open serial port in following way to make sure DTR isn't asserted, which would reset the arduino
        self.s = serial.Serial()
        self.s.setPort(port)
        try:
            self.s.setDTR(False)
        except Exception:
            pass
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
            time.sleep(0.001)
        return resp

    def parse_reply(self,reply):
        lines = reply.splitlines()
        for line in lines:
            if line.startswith('R'):
                parts = line.split()
                if len(parts) != 2:
                    raise ValueError("Couldn't parse reply: %s" % reply)
                return int(parts[1])

    def _get_position(self,axis):
        return self.parse_reply(self.sendget("C9 %d\n" % axis))

    def get_position(self):
        return self._get_position(0),self._get_position(1)

    def get_status(self):
        st0 = self.parse_reply(self.sendget("C31 0\n"))
        st1 = self.parse_reply(self.sendget("C31 1\n"))
        return self.decode_status_bits(st0),self.decode_status_bits(st1)

    def get_limits(self):
        return self.parse_reply(self.sendget("C36 0\n"))

    def decode_status_bits(self,status_reg):
        bits = StatusBits()
        bits.over_current = not (status_reg & 0x1000)
        bits.thermal_shutdown = not (status_reg & 0x0800)
        bits.thermal_warning = not (status_reg & 0x0400)
        bits.under_voltage = not (status_reg & 0x0200)
        bits.wrong_command = bool(status_reg & 0x0100)
        bits.cant_perform_command = bool(status_reg & 0x0080)
        bits.dir = bool(status_reg & 0x0010)
        bits.hiz = bool(status_reg & 0x0001)
        return bits


    def _wait_while_active(self,axis,timeout=10):
        self.sendget(("C24 %d\n" % axis),timeout=timeout)
    def wait_while_active(self,timeout=30):
        self._wait_while_active(0,timeout=timeout)
        self._wait_while_active(1,timeout=timeout)

    def _go_to_position(self,axis,position):
        self.sendget("C12 %d %d\n" % (axis,position))

    def go_to_position(self,x,y,block=True):
        if x > 7000:
            raise ValueError("Cannot safely go to x locations higher than 7000")
        if y > 4500:
            raise ValueError("Cannot safely go to y locations higher than 4500")
        self._go_to_position(0,x)
        self._go_to_position(1,y)
        if block:
            self.wait_while_active()

    def hwp_go_to_position(self,position,stop=True):
        self._go_to_position(0,position)
        if stop:
            self.wait_while_active()
            self.hard_stop()

    def initialize(self,acceleration=200,min_speed=200,max_speed=400,stepping=4):
        for axis in [0,1]:
            self.set_acceleration(acceleration,axis=axis)
            self.set_speed(min_speed,max_speed,axis=axis)
            self.set_speed(min_speed,max_speed,axis=axis)
            self.set_stepping(stepping)

    def initialize_hwp(self,acceleration=2000,min_speed=800,max_speed=8000,stepping=16):
        axis = 0
        self.set_acceleration(acceleration,axis=axis)
        self.set_speed(min_speed,max_speed,axis=axis)
        self.set_speed(min_speed,max_speed,axis=axis)
        self.set_stepping(stepping)


    def find_home(self):
        self.reset_home()
        self._find_home(stepsize=400)
        self.go_to_position(200,200)
        self.reset_home()
        self._find_home(stepsize=40)
        self.go_to_position(100,100)
        self.reset_home()
        self._find_home(stepsize=4)
    def _find_home(self,stepsize=40):
        xdone = not(self.get_limits() & 0x02)
        ydone = not(self.get_limits() & 0x08)
        x = 0
        y = 0
        self.go_to_position(x,y)
        while not (xdone and ydone):
            if not xdone:
                x -= stepsize
            if not ydone:
                y -= stepsize
            self.go_to_position(x,y)
            xdone = not(self.get_limits() & 0x02)
            ydone = not(self.get_limits() & 0x08)
        self.reset_home()

    def reset_home(self):
        self.sendget("C19 0\n")
        self.sendget("C19 1\n")

    def reset(self):
        self.go_to_position(-3000,-3000)
        self.reset_home()

    def reset_stages(self):
        self.sendget("C15 0\n")

    def set_stepping(self,microsteps):
        if microsteps not in [1,2,4,8,16]:
            raise ValueError("Invalid number of microsteps, must be 1,2,4,8,16")
        self.sendget("C34 0 %d\n" % microsteps)
        self.sendget("C34 1 %d\n" % microsteps)

    def set_speed(self,min,max=None,axis=0):
        if max is None:
            max = min
        self.sendget("C21 %d %d\n" % (axis, max))
        self.sendget("C22 %d %d\n" % (axis, min))
        actual_max = self.parse_reply(self.sendget("C7 %d\n" % axis))
        actual_min = self.parse_reply(self.sendget("C8 %d\n" % axis))
        return actual_min,actual_max

    def set_acceleration(self,accel,axis=0):
        self.sendget("C17 %d %d\n" % (axis,accel))
        self.sendget("C18 %d %d\n" % (axis,accel))
        actual_accel = self.parse_reply(self.sendget("C1 %d\n" % axis))
        actual_decel = self.parse_reply(self.sendget("C3 %d\n" % axis))
        return actual_decel,actual_accel

    def hard_stop(self):
        self.sendget("C13 0\n")
        self.sendget("C13 1\n")
