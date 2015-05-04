__author__ = 'gjones'
import stage
s = stage.Stage()
s.set_stepping(2)
print s.set_acceleration(100)
s.set_speed(200,2000,axis=0)
s.set_speed(200,2000,axis=0)
s.set_speed(200,2000,axis=1)
s.set_speed(200,2000,axis=1)
x = 0
while s.get_limits() & 0x08:
    s.go_to_position(0,x)
    x -= 10
    print x,s.get_limits()
s.reset_home()
x = 0
while s.get_limits() & 0x02:
    s.go_to_position(x,0)
    x -= 10
    print x,s.get_limits()
s.reset_home()

while True:
    s.go_to_position(5000,5000)
    s.go_to_position(0,0)
