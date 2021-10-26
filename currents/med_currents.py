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
import cartopy.feature as cfeature
import cartopy.crs as ccrs
from scipy.interpolate import griddata, interp2d
import matplotlib.pyplot as plt
import xarray as xr
import numpy as np
import warnings
import math
import sys
import pdb
import os

# disable warnings
warnings.simplefilter("ignore")

spots = {
    # known locations
    "Brindisi": [17.954848, 40.646719],
    "Campo di Mare": [18.074448, 40.539126],
    "Casalabate": [18.115720, 40.505809],
    "T. Rinalda": [18.163854, 40.480910],
    "T. Chianca": [18.201003, 40.468293],
    "Frigole":[18.251358, 40.433832],
    "San Cataldo":[18.306412, 40.388705], 
    "San Foca":[18.400512, 40.304468], 
    "Roca":[18.417373, 40.286052], 
    "Otranto":[18.488300, 40.147917], 
    "Porto Miggiano":[18.445492, 40.032193], 
    "Andrano":[18.407593, 39.971911],
    "Tricase Porto": [18.393600, 39.919967],
    "S. M. Leuca": [18.357272, 39.795486],
    "Gallipoli": [17.984831, 40.058992 ],
    "Santa Caterina": [17.979134, 40.141379],
    "S. M. al Bagno": [17.995806, 40.127617],
    "T. Inserraglio": [17.925671, 40.186565],
    "Porto Cesareo": [17.885052, 40.264565],
    "Campomarino": [17.563060, 40.297644],
    "S. P. in Bevagna": [17.678444, 40.304075]
}

# constants
appName = "[MFS_CUR_plot]"
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
    
        # initialise image
        fig = plt.figure(figsize=(15,7))
        ax = plt.axes(projection=ccrs.PlateCarree())
        
        # set boundaries
        extent = [16.9, 18.6, 39.7, 40.7]
        ax.set_extent(extent)

        # features
        ax.add_feature(cfeature.OCEAN, zorder=0)
        ax.add_feature(cfeature.LAND, zorder=1)
        ax.add_feature(cfeature.LAKES, zorder=2)
        
        # read data to be plot
        latPlot = inputFileDesc.lat[:]
        lonPlot = inputFileDesc.lon[:]        
        u = inputFileDesc.uo[0][0]
        v = inputFileDesc.vo[0][0]
        data = np.sqrt(np.square(u) + np.square(v))
        
        # plot vector norm
        x = np.linspace(min_lon, max_lon, len(lonPlot))
        y = np.linspace(min_lat, max_lat, len(latPlot))
        xx, yy = np.meshgrid(x,y)
        im = ax.contourf(xx, yy, data, 750, cmap='jet')
        
        for spot in spots:
            ax.plot(spots[spot][0], spots[spot][1], 'bo', markersize=4, transform=ccrs.Geodetic(), color="#21001a")
            ax.text(spots[spot][0], spots[spot][1], spot, transform=ccrs.Geodetic(), color="#444444", size="small")
            
        # Plot title
        plt.title("MFS Currents for date YYYY/MM/DD at 00:00 (PD=YYYYMMDD)")
        
        # Plot arrows
        print(" === Plotting arrows")
        ax.quiver(x, y, u, v, scale=25)
        
        # colorbar
        print(" === Plotting colorbar")
        plt.colorbar(im)

        # determine output filename
        date = str(inputFileDesc.time[t].data).split("T")[0]
        time = str(inputFileDesc.time[t].data).split("T")[1].split(":")[0]
        outputFile = "mfs_cur_%s_%s.png" % (date, time)
        prodDate = inputFileDesc.attrs["bulletin_date"]
        prodDate = "%s-%s-%s" % (prodDate[0:4], prodDate[4:6], prodDate[6:8])
        
        # save
        print(" === Saving image to file")        
        plt.savefig(outputFile)
           
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
        if ("MFSeas6" in f) and ("RFVL" in f):
            print(f"{appName} -- Will process file {f}")
            fileList.append(os.path.join(dataPath, f))

    # process files
    for f in fileList:
        processFile(f)
        break
