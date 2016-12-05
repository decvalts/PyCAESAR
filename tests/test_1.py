# -*- coding: utf-8 -*-
"""
Created on Mon Dec  5 15:55:11 2016

@author: dav

Test
"""

import caesarplotlib.timeseriesplot as cpl


data_dir = "/mnt/SCRATCH/Analyses/Topmodel_Sensitivity/Ryedale_storms_calibrate/"

external_file_data = "Ryedale72hours_measured.csv"

# OOP way
topmodelSensitivity = cpl.CaesarTimeseriesPlot(data_dir, "*.dat", "q_lisflood",
                                               time_delta=60,
                                               time_label='days',
                                               colormap='winter')
topmodelSensitivity.plot_ensemble_hydrograph(draw_inset=False)
topmodelSensitivity.plot_external_data(data_dir + external_file_data)
topmodelSensitivity.plot_legend()
