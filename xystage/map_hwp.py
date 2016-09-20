import numpy as np
import netCDF4
import os
from matplotlib import pyplot as plt
import time
import stage
from equipment.srs.lockin import Lockin
from equipment.hittite.signal_generator import Hittite



xy_start = (9700,1800)

steps_per_mm = 80.

x_steps = np.arange(-2000,2001,200) + xy_start[0]
y_steps = np.arange(-2000,2001,200) + xy_start[1]

hwp_steps = np.arange(0,432,4)

mmw_frequencies = np.linspace(140e9,161e9,500)


class Mapper():
    def __init__(self, use_hittite=False):
        self.stage = stage.Stage('/dev/ttyACM1')
        self.stage.initialize()
        self.hwp = stage.Stage('/dev/ttyACM0')
        self.hwp.initialize_hwp(acceleration=16000, min_speed=30,max_speed=100,stepping=2)
        # self.stage.find_home()
        self.lockin = Lockin('/dev/ttyUSB3')
        self._have_found_home = False
        if use_hittite:
            self.hittite = Hittite()
        else:
            self.hittite = None


    def do_simple_map(self, xsteps=x_steps, ysteps=y_steps,
                      settle_time=0.3, hwp_steps=hwp_steps, mmw_frequencies = np.array([-1]), description="",
                      suffix="", time_constant_wait=0.1):
        if mmw_frequencies[0]!=-1 and self.hittite is None:
            raise Exception("Need Hittite for mmw_frequencies other than -1")
        if self.hittite:
            self.hittite.set_power(0.0)
            self.hittite.on()
        if not self._have_found_home:
            print "homing..."
            self.stage.find_home()
            self.stage.find_home()
            self._have_found_home = True

        mapfile = MapDataFile(xsteps,ysteps,hwp_steps,mmw_frequencies=mmw_frequencies,suffix=suffix)
        mapfile.group.description = description
        #mapfile.group.microstepping =
        self.mapfile = mapfile
        total_measurements = len(xsteps)*len(ysteps)*len(hwp_steps)
        measured_so_far = 0
        start_time = time.time()

        for y in range(len(ysteps)):
            if y % 2:
                direction = -1
            else:
                direction = 1
            ystep = ysteps[y]
            for x in range(len(xsteps))[::direction]:
                xstep = xsteps[x]
                self.stage.go_to_position(xstep, ystep)
                if x % 2:
                    hwp_dir = -1
                else:
                    hwp_dir = 1
                for hwp_index in range(len(hwp_steps))[::hwp_dir]:
                    self.hwp._go_to_position(0,hwp_steps[hwp_index])
                    self.hwp._wait_while_active(0)
                    time.sleep(settle_time)
                    for mmw_index,mmw_frequency in enumerate(mmw_frequencies):
                        #z, _, r, theta = self.lockin.get_data()
                        try:
                            self.hittite.set_freq(mmw_frequency/12.0)
                        except AttributeError:
                            if mmw_frequencies[0] != -1:
                                raise Exception("Unable to communicate with hittite, but mmw frequency was requested")
                        time.sleep(time_constant_wait)
                        try:
                            r,theta = self.lockin.snap(3,4)
                        except:
                            print "lockin error"
                            r,theta = np.nan,np.nan
                        mapfile.z[x,y,hwp_index,mmw_index] = r
                        mapfile.nc.sync()
                        print x, y, hwp_index, mmw_frequency, r
                    measured_so_far +=1
                    time_so_far = time.time()-start_time
                    time_per_point = time_so_far/measured_so_far
                    time_remaining = time_per_point*(total_measurements-measured_so_far)
                    print "%.1f minutes remaining, finish at %s" % (time_remaining/60.,time.ctime(time.time()+time_remaining))
        self.hwp.hard_stop()

def create_new_netcdf_file(base_dir='/data/readout/hwp_mapping', suffix=''):
    ase_dir = os.path.expanduser(base_dir)
    if not os.path.exists(base_dir):
        try:
            os.mkdir(base_dir)
        except Exception, e:
            raise Exception("Tried to make directory %s for data file but failed. Error was %s" % (base_dir, str(e)))
    fn = time.strftime('%Y-%m-%d_%H%M%S')
    if suffix:
        suffix = suffix.replace(' ', '_')
        fn += ('_' + suffix)
    fn += '.nc'
    fn = os.path.join(base_dir, fn)
    filename = fn
    nc = netCDF4.Dataset(fn, mode='w')
    return nc,filename


class MapDataFile():
    def __init__(self, x, y, hwp_steps, mmw_frequencies=np.array([-1]), parent_nc = None,suffix=''):
        x = np.atleast_1d(x)
        y = np.atleast_1d(y)
        hwp_steps = np.atleast_1d(hwp_steps)
        mmw_frequencies = np.atleast_1d(mmw_frequencies)
        if parent_nc is None:
            nc,filename = create_new_netcdf_file(suffix=suffix)
            parent_nc = nc
            print "created",filename
        self.nc = parent_nc
        group_name = time.strftime('map_%Y%m%d%H%M%S')
        group = parent_nc.createGroup(group_name)
        self.group = group
        group.createDimension('x', x.shape[0])
        group.createDimension('y', y.shape[0])
        group.createDimension('hwp_step', hwp_steps.shape[0])
        group.createDimension('mmw_frequency', mmw_frequencies.shape[0])
        self.x = group.createVariable('x', np.float, dimensions=('x',))
        self.y = group.createVariable('y', np.float, dimensions=('y',))
        self.hwp_step = group.createVariable('hwp_step', np.float, dimensions=('hwp_step',))
        self.mmw_frequency = group.createVariable('mmw_frequency', np.float, dimensions=('mmw_frequency',))
        self.z = group.createVariable('z', np.float, dimensions=('x', 'y','hwp_step','mmw_frequency'))
        self.x[:] = x
        self.y[:] = y
        self.hwp_step[:] = hwp_steps
        self.mmw_frequency[:] = mmw_frequencies

