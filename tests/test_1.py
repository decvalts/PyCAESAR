# -*- coding: utf-8 -*-
"""
Created on Mon Dec  5 15:55:11 2016

@author: dav

Test
"""

import caesarplotlib.timeseriesplot as cpl


data_dir = "/mnt/SCRATCH/Analyses/RegressionTest/final_regression_test_intel_gcc/"
#data_dir = "/run/media/dav/SHETLAND/Analyses/HydrogeomorphPaper/BOSCASTLE/Analysis/"
#data_dir="/mnt/WORK/Dev/PyToolsPhD/Radardata_tools"
#data_dir = "/mnt/SCRATCH/Analyses/Topmodel_Sensitivity/Ryedale_storms_calibrate/"

input_raster2 = "elev.txt"
input_raster1 = "elevdiff.txt"
# input_raster2 = "rainfall_totals_boscastle_downscaled.asc"

# A text file with x, y scatter values, in case of future use
outpt_datafile_name = "elev_vs_erosion.txt"

fname = "boscastle_lumped_detachlim.dat"
wildcard_fname = "ryedale_*.dat"

external_file_data = "Ryedale72hours_measured.csv"


# plot_hydrograph(data_dir, fname, "q_lisflood", draw_inset=True)


time_delta = 60
# time delta is the difference between output time steps in the
# .dat file (minutes)
# You must know this beforehand, i.e. it can't be calculated
# from the timeseries file alone.

# OOP way
SwaleHydroS = cpl.CaesarTimeseriesPlot(data_dir, "*.dat", "q_lisflood",
                                       time_delta=time_delta,
                                       time_label='days',
                                       colormap='jet')

SwaleHydroS.plot_ensemble_hydrograph(draw_inset=False, labellines=False)
# BosHydroS.plot_external_data(data_dir + external_file_data)
SwaleHydroS.ax.ticklabel_format(axis='y', style='sci', scilimits=(-2, 2))
SwaleHydroS.ax.yaxis.get_offset_text().set_visible(False)
SwaleHydroS.plot_legend()
