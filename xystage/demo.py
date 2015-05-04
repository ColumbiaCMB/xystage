__author__ = 'gjones'
import stage
s = stage.Stage()
s.set_stepping(2)
print s.set_acceleration(10000)
s.set_speed(200,2000,axis=0)
s.set_speed(200,2000,axis=0)
s.set_speed(200,2000,axis=1)
s.set_speed(200,2000,axis=1)
while True:
    for k in [100,500,1000,5000]:
        print '%s\n%s' % s.get_status()
        s.set_acceleration(k,axis=0)
        s.set_acceleration(k,axis=1)
        s.go_to_position(0,0)
        s.go_to_position(350,350)
    for k in range(1):
        s.go_to_position(0,0)
        s.go_to_position(350,350)