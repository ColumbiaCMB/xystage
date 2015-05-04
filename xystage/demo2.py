__author__ = 'gjones'
import stage
s = stage.Stage()
s.set_stepping(2)
print s.set_acceleration(100)
s.set_speed(200,2000,axis=0)
s.set_speed(200,2000,axis=0)
s.set_speed(200,2000,axis=1)
s.set_speed(200,2000,axis=1)
while True:
    for x in range(0,351,10):
        s.go_to_position(x,x)
    print "turning"
    for x in range(0,351,10)[::-1]:
        s.go_to_position(x,x)
