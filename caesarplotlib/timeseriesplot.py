# -*- coding: utf-8 -*-
"""
Caesar Lisflood timeseries plotting tools

This module is for plotting output fromt the CAESAR-Lisflood model timeseries files
(i.e. the .dat file from a simulation, if you've stuck with the default naming convention.)

:author: DAV
"""
import glob
import os
import re  # regex
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

from mpl_toolkits.axes_grid1.inset_locator import zoomed_inset_axes
from mpl_toolkits.axes_grid1.inset_locator import mark_inset

import labellines


# Plotting parameters
rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['arial']
rcParams['font.size'] = 16


def create_data_arrays(data_dir, input_raster1, input_raster2):
    """This function creates data arrays from two input rasters.

    :param data_dir: The path to your rasters
    :param input_raster1: The name of raster 1, with extension
    :param input_raster2: The name of raster 2, with extension
    :returns: Two numpy arrays, containing the raster data.
    :author: DAV
    """
    load_data1 = data_dir + "/" + input_raster1
    load_data2 = data_dir + "/" + input_raster2
    data_raster1 = np.loadtxt(load_data1, skiprows=6)
    data_raster2 = np.loadtxt(load_data2, skiprows=6)

    # get a 1D array from the raster data.
    return data_raster1.flatten(), data_raster2.flatten()


def plot_scatter_rasterdata(data_array1, data_array2):
    """Plots data from a raster dataset as an x-y scattergraph.
    
    So if you have two rasters, one of elevation, and one of erosion,
    you could plot erosion amount as a function of elevation.
    
    :param data_array1: A numpy array
    :param data_array2: Another numpy array
    """
    plt.scatter(data_array1, data_array2, marker="x")
    plt.xlim(0, 300)
    # plt.ylim(0,1400)
    plt.xlabel("Elevation (m)")
    plt.ylabel("Elevation difference (mm)")
    plt.show()


def convert_timestep(time_step, time_delta, time_label):
    """This converts a unitless timestep from model output, for example, 
    into one with units based on the difference between timesteps and the
    time unit
    """
    # Supported time formats: minutes, hours, days, years

    minutes = time_step*time_delta
    hours = minutes/60
    days = hours/24
    years = days/365.25

    dic = {'minutes': minutes,
           'hours': hours,
           'days': days,
           'years': years
           }

    if time_label not in dic:
      raise ValueError( "Your selected time units are not supported: %s" % time_label )

    return dic[time_label]


class CaesarTimeseriesPlot(object):
    """This class creates objects composed of matplotlib figures and axes,
    that display the timeseries plotted data.
    
    There are methods for extracting data from input files, and plotting it in
    different formats.
    """

    def __init__(self, data_dir, fname, datametric, time_delta=60, time_label='hours',
                 colormap='jet'):
        self.data_dir = data_dir
        self.fname = fname
        self.fig, self.ax = plt.subplots()
        self.time_delta = time_delta # timestep in the .dat file
        self.time_label = time_label # Units that will appear on the graph
        self.colormap = colormap

        self.ax_inset = None
        self.metric_name = datametric
        self.num_graphs = len(glob.glob(self.data_dir + self.fname))

    """
    Extracts the relevant data column from the timeseries file.
    """
    def get_datametric_array(self, filename, data_name):
        """Reads data into an array from a filename,
        which should be the caesar-lisflood output file. (.dat")
        
        :param filename: Full path to the filename
        :param data_name: Name of the measurement you want to plot.
        
        Supported metrics (data_name) are:
            time_step
            q_losflood
            q_topmodel
            sed_tot
            d1, d2, d3, ..., d9 (i.e. Grain size fraction amounts)
            cumulative_sed_tot
        """
        time_step, \
        q_lisflood, \
        q_topmodel, \
        sed_tot, \
        d1, d2, d3, d4, d5, \
        d6, d7, d8, d9 = np.loadtxt(filename,
                                    usecols=(0, 1, 2, 4, 5, 6, 7,
                                             8, 9, 10, 11, 12, 13),
                                             unpack=True)
        cumulative_sed_tot = np.cumsum(sed_tot)

        # Create a dictionary to store the keys/arrays
        # You can add to this later without having to modify
        # the plot_hydrography function
        dic = {'q_lisflood': q_lisflood,
               'q_topmodel': q_topmodel,
               'sed_tot': sed_tot,
               'd1': d1,
               'd2': d2,
               'd3': d3,
               'd4': d4,
               'd5': d5,
               'd6': d6,
               'd7': d7,
               'd8': d8,
               'd9': d9,
               # Special calls (not in raw data file)
               'cumulative_sed_tot': cumulative_sed_tot,
               }
        return time_step, dic[data_name]

    def plot_hydrograph(self, current_timeseries=None,
                        draw_inset=False, ax_inset=None):
        """Plots a hydrograph"""
        if current_timeseries is None:
            current_timeseries = self.fname

        line_label = self.make_line_label(current_timeseries)

        filename = self.data_dir + current_timeseries
        # get the time step array and the data metric
        # you want to plot against it.
        time_step, metric = self.get_datametric_array(filename, self.metric_name)
        time_units = convert_timestep(time_step, self.time_delta, self.time_label)

        # If we want to draw the inset,
        # and we haven't already got an inset axes
        # i.e. if you were using the multiple plot/ensemble plot,
        # this would already have been created.
        if (draw_inset is True and self.ax_inset is None):
            self.ax_inset = self.create_inset_axes()

        # plot the main axes data
        line, = self.ax.plot(time_units, metric, linewidth=1.5, alpha=0.5)
        line.set_label(line_label)
        #labelLine(line, 45)

        # Tweak the xlimits to zone in on the relevnat bit of hydrograph
        #self.ax.set_xlim(0, 900)
        #self.ax.set_ylim(0,60)

        # Now plot the inset data
        if self.ax_inset is not None:
            self.plot_inset(time_units, metric)



    def plot_ensemble_hydrograph(self, draw_inset=False, labellines=False):
        """Plots multiple hydrographs on the same axes"""

        cm = plt.get_cmap(self.colormap)
        self.ax.set_color_cycle([cm(1.*i/self.num_graphs)
                               for i in range(self.num_graphs)])

        if draw_inset is True:
            self.ax_inset = self.create_inset_axes()
        else:
            self.ax_inset = None

        # Loop through the files in a dir and plot them all on the same axes
        for f in sorted(glob.glob(self.data_dir + self.fname)):
            current_timeseries = os.path.basename(f)
            print current_timeseries
            self.plot_hydrograph(current_timeseries, draw_inset)

        # for i in caesar_cube.dim(3) # loop through 3rd dims of array

        # draw a bbox of the region of the inset axes in the parent axes and
        # connecting lines between the bbox and the inset axes area
        # mark_inset(ax, ax_inset, loc1=2, loc2=3, fc="none", ec="0.5")
        self.set_labels()

        if labellines == True:
           self.add_line_labels()

    def set_labels(self):
        """ Returns formatted labels from a dictionary based on the data_name supplied
        in get_data_metric_array()
        """

        label_dic = {
          'q_lisflood': "water discharge ($m^3s^{-1}$)",
          'q_topmodel': "water (TOPMODEL) discharge ($m^3s^{-1}$)",
          'sed_tot': "sediment flux ($m^3$)",
          'd1': "d1 proportion",
          'd2': "d2 proportion",
          'd3': "d3 proportion",
          'd4': "d4 proportion",
          'd5': "d5 proportion",
          'd6': "d6 proportion",
          'd7': "d7 proportion",
          'd8': "d8 proportion",
          'd9': "d9 proportion",
          'cumulative_sed_tot' : "Cumulative sediment yield ($m^3$)",
        }

        time_axis_label = 'Simulated time (' + str(self.time_label)  + ')'

        self.ax.set_xlabel(time_axis_label)
        self.ax.set_ylabel(label_dic[self.metric_name])

    def make_line_label(self, fname):
        # Passing a list of delimiters to the re.split function
        part1 = re.split("[_.]", fname)[0]
        part2 = re.split("[_.]", fname)[1]
        part3 = re.split("[_.]", fname)[2]
        part4 = re.split("[_.]", fname)[3]

        part = "M = " + part1
        print part
        return part

    def add_line_labels(self):
        """Experimental. Adds text labels to individual lines in the 
        hydrograph plots. Positioning of the labels can sometimes be a bit weird, 
        so use with trial and error.
        """
        x_pos = [44.3, 45.8, 48, 52, 56, 60]
        labellines.labelLines(self.ax.get_lines(), zorder=2.5,
                   align=True, fontsize=10, xvals=x_pos)

    def save_figure(self, save_name="test.png"):
        self.fig.savefig(save_name, bbox_inches='tight')

    def create_inset_axes(self):
        
        ax_inset = zoomed_inset_axes(self.ax, 3.5, loc=1)

        cm = plt.get_cmap(self.colormap)
        ax_inset.set_color_cycle([cm(1.*i/self.num_graphs)
                                 for i in range(self.num_graphs)])

        # hide every other tick label
        for label in ax_inset.get_xticklabels()[::2]:
            label.set_visible(False)

        return ax_inset

    def plot_inset(self, x_data, y_data):
        """Plots an inset window to show a zooomed in portion of the graph"""

        self.ax_inset.plot(x_data, y_data,alpha=0.5)
        # SHould be user settable
        self.ax_inset.set_xlim(40, 70)
        self.ax_inset.set_ylim(5, 30)

    def plot_legend(self):
        """Plots the legend"""
        self.ax.legend(#bbox_to_anchor=(1, 0.4),
               #loc='center left', prop={'size': 11})
               loc=2, prop={'size': 11})

    def showfig(self):
        """
        Note: this will only work in GUI. If you are using an IPython
        console session, for example, just type CatchmentPlot.fig to re-draw
        the figure in the console.
        """
        self.fig.show()

    def plot_external_data(self, filename):
        """
        Plots external data, such as recorded discharge from
        a gauging station
        """
        x, y = np.loadtxt(filename, unpack=True, delimiter=',')
        hours = convert_timestep(x, self.time_delta, self.time_label)
        line, = self.ax.plot(hours, y, '--k', linewidth=2)
        line.set_label("Measured")
