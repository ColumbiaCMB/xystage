__author__ = 'gjones'
import mapview
import netCDF4
import glob
from matplotlib import pyplot as plt

files = glob.glob('/home/data/beams/*.nc')
files.sort()

mapview.MapFileViewer(files[-1])
plt.show()
"""
nc = netCDF4.Dataset(files[-1],mode='r')

group = nc.groups[nc.groups.keys()[0]]

x = group.variables['x'][:]
y = group.variables['y'][:]
z = group.variables['z'][:,:,0]


viewer = viewxy.Viewer2d(z,x,y)
plt.show()
"""