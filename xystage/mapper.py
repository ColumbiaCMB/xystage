import numpy as np
import netCDF4
import os
from matplotlib import pyplot as plt
import time
import stage
from kid_readout.equipment.lockin_controller import lockinController
from kid_readout.equipment.hittite_controller import hittiteController


class Mapper():
    def __init__(self):
        self.stage = stage.Stage()
        self.stage.initialize()
        # self.stage.find_home()
        self.lockin = lockinController(serial_port='/dev/ttyUSB3')
        self.hittite = None

    def do_simple_map(self, xsteps=np.arange(0, 10000, 1000), ysteps=np.arange(0, 10000, 1000),
                      settle_time=0.1, mmw_source_frequencies=-1, description="",suffix=""):
        # self.stage.find_home()
        if np.isscalar(mmw_source_frequencies):
            mmw_source_frequencies = np.array([mmw_source_frequencies])
        # if CW mode is used, frequency is > 0
        if mmw_source_frequencies[0] > 0:
            if self.hittite is None:
                self.hittite = hittiteController()
                self.hittite.set_power(0)
                self.hittite.on()

        mapfile = MapDataFile(xsteps,ysteps,mmw_source_frequencies,suffix=suffix)
        mapfile.group.description = description
        #mapfile.group.microstepping =
        self.mapfile = mapfile

        for y in range(len(ysteps)):
            if y % 2:
                direction = -1
            else:
                direction = 1
            ystep = ysteps[y]
            for x in range(len(xsteps))[::direction]:
                xstep = xsteps[x]
                self.stage.go_to_position(xstep, ystep)
                for freq_index,freq in enumerate(mmw_source_frequencies):
                    if freq > 0:
                        self.hittite.set_freq(freq/12.0)
                    time.sleep(settle_time)
                    z, _, r, theta = self.lockin.get_data()
                    mapfile.z[x,y,freq_index] = z
                    mapfile.nc.sync()
                    print x, y, freq, z


def create_new_netcdf_file(base_dir='/home/data/beams', suffix=''):
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
    def __init__(self, x, y, frequency, parent_nc = None,suffix=''):
        if np.isscalar(frequency):
            frequency = np.array([frequency])
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
        group.createDimension('frequency', frequency.shape[0])
        self.x = group.createVariable('x', np.float, dimensions=('x',))
        self.y = group.createVariable('y', np.float, dimensions=('y',))
        self.frequency = group.createVariable('frequency', np.float, dimensions=('frequency',))
        self.z = group.createVariable('z', np.float, dimensions=('x', 'y','frequency'))

        self.x[:] = x
        self.y[:] = y
        self.frequency[:] = frequency


