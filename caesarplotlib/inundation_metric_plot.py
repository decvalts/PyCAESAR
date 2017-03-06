#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  6 12:31:03 2017

Plots ensemble graphs from the inundation metric generator

@author: dav
"""

import numpy as np
import matplotlib.pyplot as plt
import glob
import re
import os


file_wildcard = "/mnt/SCRATCH/Analyses/InundationAnalysis/BoscastleInundation/boscastle_inundation_*.txt"

def make_line_label(fname):
    # Passing a list of delimiters to the re.split function
    
    basename = os.path.splitext(os.path.basename(fname))
    print(basename)
    parts = re.split("[_]", basename[0])

    #part = basename[0] + '_' + basename[1]
    print(parts[2] + '_' + parts[3])
    label = parts[2] + '_' + parts[3]
    return label

for file in glob.glob(file_wildcard):
    print(file)
    timestep, inundation_area, catchment_depth, floodplain_depth, channel_depth = \
      np.loadtxt(file, usecols=(0,1,2,3, 4) , unpack=True)
    
    label = make_line_label(file)
    line, = plt.plot(timestep, channel_depth)
    line.set_label(label)

  
plt.legend()
    