__author__ = 'gjones'
import stage
s = stage.Stage()
s.set_stepping(2)
print s.set_acceleration(10000)
s.set_speed(200,2000)
s.set_speed(200,2000)
while True:
    for k in [100,500,1000,5000,10000,20000,30000,40000]:
        print s.set_acceleration(k)
        s.go_to_position(0,0)
        s.go_to_position(350,0)
    for k in range(10):
        s.go_to_position(0,0)
        s.go_to_position(350,0)