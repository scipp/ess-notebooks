import os
import sys

import ess.v20.imaging as imaging
import ess.v20.imaging.operations as operations
import ess.wfm as wfm

import dataconfig
import scipp as sc
import numpy as np

from scipy import ndimage, signal

local_data_path = os.path.join('ess', 'v20', 'imaging', 'gp2-stress-experiments')
data_dir = os.path.join(dataconfig.data_root, local_data_path)
output_dir = os.path.join(dataconfig.data_root, 'output')
instrument_file = os.path.join(data_dir, 'V20_Definition_GP2.xml')

tofs_path = os.path.join(data_dir, 'GP2_Stress_time_values.txt')
raw_data_dir = os.path.join(data_dir)

if not os.path.exists(data_dir):
    raise FileNotFoundError("The following data directory does not exist,"
                            f" check your make_config.py:\n{data_dir}")


# Load tiff stack
def load_and_scale(folder_name, scale_factor):
    to_load = os.path.join(raw_data_dir, folder_name)
    variable = imaging.tiffs_to_variable(to_load, dtype=np.float32)
    variable *= scale_factor
    return variable


def load():

    # Pulse references
    pulse_number_reference = 1.0 / 770956
    pulse_number_sample = 1.0 / 1280381
    pulse_number_sample_elastic = 1.0 / 2416839
    pulse_number_sample_plastic = 1.0 / 2614343

    # units of transmission, all pixels with transmission higher masking threshold are masked
    masking_threshold = 0.80

    # Toggles outputting masked and sliced tiff stacks
    output_tiff_stack = False

    # Experiment Metadata
    measurement_number = 11

    # Load time bins from 1D text file
    ds = sc.Dataset()
    ds.coords["t"] = sc.Variable(["t"],
                                 unit=sc.units.us,
                                 values=imaging.read_x_values(tofs_path, skiprows=1, usecols=1, delimiter='\t'),)
    ds.coords["t"] *= 1e3


    ds["reference"] = load_and_scale(folder_name="R825-open-beam",
                                     scale_factor=pulse_number_reference)
    ds["sample"] = load_and_scale(folder_name="R825",
                                  scale_factor=pulse_number_sample)
    ds["sample_elastic"] = load_and_scale(folder_name="R825-600-Mpa",
                                          scale_factor=pulse_number_sample_elastic)


    # Geometry
    geometry = sc.Dataset()
    sc.compat.mantid.load_component_info(geometry, instrument_file)
    geom = sc.Dataset(coords={"sample-position": geometry.coords["sample-position"],
                              "source-position": geometry.coords["source-position"]})
    geom.coords["position"] = sc.reshape(geometry.coords['position'], dims=['y', 'x'],
                                         shape=tuple(ds["sample"]["t", 0].shape))
    geom.coords["x"] = sc.geometry.x(geom.coords["position"])["y", 0]
    geom.coords["y"] = sc.geometry.y(geom.coords["position"])["x", 0]
    ds = sc.merge(ds, geom)
    ds

    return ds