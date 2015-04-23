__author__ = 'gjones'
import stage
s = stage.Stage()
s.set_stepping(2)
print s.set_acceleration(100)
s.set_speed(50,200)
s.set_speed(50,200)
while True:
    for x in range(0,351,10):
        s.go_to_position(x,x)
    print "turning"
    for x in range(0,351,10)[::-1]:
        s.go_to_position(x,x)
