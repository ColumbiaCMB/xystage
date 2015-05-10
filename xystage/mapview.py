# based on: http://scipy-central.org/item/22/4/building-a-simple-interactive-2d-data-viewer-with-matplotlib
import os
import time

__author__ = 'gjones'

import netCDF4
from matplotlib.widgets import Cursor, Button
import matplotlib.pyplot as plt
import numpy as np
plt.rcParams['font.size']=8


class Viewer2d(object):
    def __init__(self,z,x=None, y=None):
        """
        Shows a given array in a 2d-viewer.
        Input: z, an 2d array.
        x,y coordinters are optional.
        """
        if x is None:
            self.x=np.arange(z.shape[0])
        else:
            self.x=x
        if y is None:
            self.y=np.arange(z.shape[1])
        else:
            self.y=y
        self.z=z
        self.fig=plt.figure()
        #Doing some layout with subplots:
        self.fig.subplots_adjust(0.05,0.05,0.98,0.98,0.1)
        self.overview=plt.subplot2grid((8,4),(0,0),rowspan=7,colspan=2)
        self.quad = self.overview.pcolormesh(self.x,self.y,self.z)
        print self.quad.get_array().shape
        self.overview.autoscale(1,'both',1)
        self.x_subplot=plt.subplot2grid((8,4),(0,2),rowspan=4,colspan=2)
        self.y_subplot=plt.subplot2grid((8,4),(4,2),rowspan=4,colspan=2)
        self.xline, = self.x_subplot.plot(self.x,z[z.shape[0]//2,:])
        self.yline, = self.y_subplot.plot(self.y,z[:,z.shape[0]//2])


        #Adding widgets, to not be gc'ed, they are put in a list:

        cursor=Cursor(self.overview, useblit=True, color='black', linewidth=2 )
        but_ax=plt.subplot2grid((8,4),(7,0),colspan=1)
        reset_button=Button(but_ax,'Reset')
        but_ax2=plt.subplot2grid((8,4),(7,1),colspan=1)
        legend_button=Button(but_ax2,'Legend')
        self._widgets=[cursor,reset_button,legend_button]
        #connect events
        reset_button.on_clicked(self.clear_xy_subplots)
        legend_button.on_clicked(self.show_legend)
        self.fig.canvas.mpl_connect('button_press_event',self.click)
        self.fig.canvas.mpl_connect('motion_notify_event',self.motion)

    def show_legend(self, event):
        """Shows legend for the plots"""
        for pl in [self.x_subplot,self.y_subplot]:
            if len(pl.lines)>0:
                pl.legend()
        plt.draw()

    def clear_xy_subplots(self,event):
        """Clears the subplots."""
        self.overview.lines = []
        for j in [self.x_subplot,self.y_subplot]:
            j.lines = j.lines[:1]
            j.legend_ = None
        plt.draw()
    def update_data(self,event):
        pass
    def motion(self,event):
        if event.inaxes == self.overview:
            xpos=np.argmin(np.abs(event.xdata-self.x))
            ypos=np.argmin(np.abs(event.ydata-self.y))
            self.xline.set_ydata(self.z[ypos,:])
            self.yline.set_ydata(self.z[:,xpos])
            plt.draw()

    def click(self,event):
        """
        What to do, if a click on the figure happens:
            1. Check which axis
            2. Get data coord's.
            3. Plot resulting data.
            4. Update Figure
        """
        if event.inaxes==self.overview:
            #Get nearest data
            xpos=np.argmin(np.abs(event.xdata-self.x))
            ypos=np.argmin(np.abs(event.ydata-self.y))

            #Check which mouse button:
            if event.button==1:
                #Plot it
                c,=self.y_subplot.plot(self.y, self.z[:,xpos],label=str(self.x[xpos]))
                self.overview.axvline(self.x[xpos],color=c.get_color(),lw=2)

            elif event.button==3:
                #Plot it
                c,=self.x_subplot.plot(self.x, self.z[ypos,:],label=str(self.y[ypos]))
                self.overview.axhline(self.y[ypos],color=c.get_color(),lw=2)

        if event.inaxes==self.y_subplot:
            ypos=np.argmin(np.abs(event.xdata-self.y))
            c,=self.x_subplot.plot(self.x, self.z[ypos,:],label=str(self.y[ypos]))
            self.overview.axhline(self.y[ypos],color=c.get_color(),lw=2)

        if event.inaxes==self.x_subplot:
            xpos=np.argmin(np.abs(event.xdata-self.x))
            c,=self.y_subplot.plot(self.y, self.z[:,xpos],label=str(self.x[xpos]))
            self.overview.axvline(self.x[xpos],color=c.get_color(),lw=2)
        #Show it
        plt.draw()

class MapFileViewer(Viewer2d):
    def __init__(self,filename):
        self.filename = filename
        x,y,z = self.get_data()
        self.freq_index = 5
        super(MapFileViewer,self).__init__(z[:,:,self.freq_index],x,y)
        self.last_mtime = os.path.getmtime(self.filename)
        self.timer = self.fig.canvas.new_timer(interval=2000)
        self.timer.add_callback(self.update_data,None)
        self.timer.start()


    def get_data(self):
        nc = netCDF4.Dataset(self.filename,mode='r')
        group = nc.groups[nc.groups.keys()[0]]
        y = group.variables['x'][:]
        x = group.variables['y'][:]
        z = group.variables['z'][:]
        nc.close()
        return x,y,z

    def update_data(self,event):
        mtime = os.path.getmtime(self.filename)
        if mtime == self.last_mtime:
            return
        self.last_mtime = mtime
        tic = time.time()
        x,y,z = self.get_data()
        self.z = z[:,:,self.freq_index]
        xlim = self.overview.get_xlim()
        ylim = self.overview.get_ylim()
        del self.overview.collections[0]
        self.quad = self.overview.pcolormesh(self.x,self.y,self.z)
        zmin = z.min()
        zmax = z.max()

        self.x_subplot.set_ylim(zmin,zmax)
        self.y_subplot.set_ylim(zmin,zmax)
#        self.overview.set_xlim(xlim)
#        self.overview.set_ylim(ylim)
        plt.draw()
        print time.time() - tic



if __name__=='__main__':
    #Build some strange looking data:
    x=np.linspace(-3,3,300)
    y=np.linspace(-4,4,400)
    X,Y=np.meshgrid(x,y)
    z=np.sqrt(X**2+Y**2)+np.sin(X**2+Y**2)
    w, h = 512, 512
    A = np.random.randn(512,512)
    #Put it in the viewer
    fig_v=Viewer2d(z,x,y)
    fig_v2=Viewer2d(A)
    #Show it
    plt.show()