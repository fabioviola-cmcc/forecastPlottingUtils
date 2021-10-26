#!/bin/bash

# module load
module load intel19.5/19.5.281 intel19.5/szip/2.1.1 intel19.5/hdf5/1.10.5 intel19.5/netcdf/C_4.7.2-F_4.5.2_CXX_4.3.1

# Invoke medslik
SCRIPT_PATH=/work/opa/witoil/plot/currents
SCRIPT_EXE=${SCRIPT_PATH}/med_currents.py
bsub -R "span[ptile=1]" -sla SC_SERIAL_witoil -Is -q s_medium -app SERIAL_witoil -P 0372 -J plot_MFS_CUR "python $SCRIPT_EXE $1 $2"
