#!/usr/bin/python3
#
#
# Error codes:
# 1 - Production date not specified
# 2 - Output folder not specified
# 3 - Output folder cannot be created
# 4 - Production date invalid
# 5 - Input file not found
#
# File structure:
# - variable of interest:
#   thetao(time, depth, lat, lon)
# - timesteps:
#   24
#

# global reqs
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import xarray as xr
import numpy as np
import traceback
import warnings
import sys
import pdb
import os

# disable warnings
warnings.simplefilter("ignore")

# constants
appName = "[MFS_SST_plot]"
dataRoot = '/data/inputs/metocean/rolling/ocean/CMCC/CMEMS/1.0forecast/1h/'


# process file 
def processFile(inputFile):

    # open NetCDF file
    print(f"{appName} -- Opening input file {inputFile}")
    try:
        inputFileDesc = xr.open_dataset(inputFile)
    except FileNotFoundError:
        print(f"{appName} -- ERROR: {inputFile} not found!")
        sys.exit(5)
        
    # get the boundaries
    min_lat = inputFileDesc.lat.min().to_dict()["data"]
    max_lat = inputFileDesc.lat.max().to_dict()["data"]
    min_lon = inputFileDesc.lon.min().to_dict()["data"]
    max_lon = inputFileDesc.lon.max().to_dict()["data"]
        
    # process all the timesteps
    for t in range(len(inputFileDesc.time)):
        print(f"{appName} -- Processing timestep {t}")

        # determine output filename
        date = str(inputFileDesc.time[t].data).split("T")[0]
        time = str(inputFileDesc.time[t].data).split("T")[1].split(":")[0]
        outputFile = "mfs_sst_%s_%s.png" % (date, time)
        prodDate = inputFileDesc.attrs["bulletin_date"]
        prodDate = "%s-%s-%s" % (prodDate[0:4], prodDate[4:6], prodDate[6:8])
        
        # create a map
        plt.figure(figsize=(20,7))
        map = Basemap(llcrnrlon=min_lon, llcrnrlat=min_lat, urcrnrlon=max_lon, urcrnrlat=max_lat, resolution="f")
        
        # draw the coastline
        map.drawcoastlines()
        map.drawparallels(np.arange(min_lat, max_lat, 2),labels=[0,0,0,0])
        map.drawmeridians(np.arange(min_lon, max_lon, 2),labels=[0,0,0,0])
            
        # plot the variable
        latPlot = inputFileDesc.lat[:]
        lonPlot = inputFileDesc.lon[:]
        data = inputFileDesc.thetao[t][0]        
        x = np.linspace(min_lon, max_lon, len(lonPlot))
        y = np.linspace(min_lat, max_lat, len(latPlot))
        xx, yy = np.meshgrid(x,y)
        map.pcolormesh(xx, yy, data, cmap='jet')
        map.colorbar(location='bottom')

        # set title
        plt.title("Sea surface temperature -- MFS \n Production Date: %s -- Reference Date and time: %s, %s:30" % (prodDate, date, time))
        
        # save
        plt.savefig(outputFile)
        print(f"{appName} -- Produced file {outputFile}")

    # close NetCDF file
    print(f"{appName} -- Closing input file {inputFile}")
    inputFileDesc.close()


# main
if __name__ == "__main__":

    # process command line arguments
    try:
        prodDate = sys.argv[1]
    except IndexError:
        print(f"{appName} -- ERROR: production date is a mandatory argument!")
        sys.exit(1)

    try:
        outFolder = sys.argv[2]
    except IndexError:
        print(f"{appName} -- ERROR: output folder is a mandatory argument!")
        sys.exit(2)

    # check if output folder exists, if not create it
    if not os.path.exists(outFolder):
        print(f"{appName} -- Output folder does not exists. Creating it...")
        try:
            os.mkdir(outFolder)
        except:
            print(f"{appName} -- ERROR: Output folder cannot be created.")
            sys.exit(3)
        
    # build the path
    dataPath = os.path.join(dataRoot, prodDate)
    print(f"{appName} -- Input path set to {dataPath}")
    print(f"{appName} -- Output path set to {outFolder}")
        
    # check if the path exists
    if not os.path.exists(dataPath):
        print(f"{appName} -- ERROR: production date not valid!")
        sys.exit(4)

    # get the list of files to process
    fileList = []
    for f in os.listdir(dataPath):
        if ("MFSeas6" in f) and ("TEMP" in f):
            print(f"{appName} -- Will process file {f}")
            fileList.append(os.path.join(dataPath, f))

    # process files
    for f in fileList:
        processFile(f)
