import time

import serial


class SimpleStepper(object):

    name = 'hwp_motor'

    def __init__(self, port='/dev/ttyACM1'):
        self.s = serial.Serial()
        self.s.setPort(port)
        # The following avoids resetting the arduino
        try:
            self.s.setDTR(False)
        except Exception:
            pass
        self.s.timeout = 0
        self.s.open()
        self.switch_state = None
        self.steps = None

    @property
    def state(self):
        return dict(steps=self.steps, index_switch=self.switch_state)

    def sendget(self, cmdstr, timeout=2):
        self.s.readlines()
        self.s.write(cmdstr)
        tic = time.time()
        resp = ''
        while time.time() - tic < timeout:
            resp += self.s.read()
            if '\n' in resp:
                break
            time.sleep(0.001)
        return resp

    def parse_response(self, response):
        try:
            part_a = response.split(':')
            steps, state = [int(x) for x in part_a[1].split()]
        except ValueError:
            raise ValueError("Unable to parse response %r" % response)
        return steps, state

    def initialize(self):
        self.sendget('r')
        steps, state = self.parse_response(self.sendget('r'))
        self.switch_state = state
        self.steps = steps
        print "switch state:", self.switch_state

    def increment(self):
        self.steps, self.switch_state = self.parse_response(self.sendget('a'))
        return self.steps, self.switch_state

    def decrement(self):
        self.steps, self.switch_state = self.parse_response(self.sendget('b'))
        return self.steps, self.switch_state

    def find_home(self):
        self.initialize()
        while self.switch_state:
            self.increment()
        while not self.switch_state:
            self.decrement()
        self.steps = 0

    def move(self, steps_to_move, verbose=False):
        if steps_to_move > 0:
            action = self.increment
        else:
            action = self.decrement
        for k in range(abs(steps_to_move)):
            result = action()
            if verbose:
                print result
        return self.steps, self.switch_state
