import os
import sys

from dress import wfm
import ess.v20.imaging as imaging
import ess.v20.imaging.operations as operations
import dataconfig
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




def load():
    # Load time bins from 1D text file
    ds = sc.Dataset()
    ds.coords["t"] = sc.Variable(["t"],
                                 unit=sc.units.us,
                                 values=imaging.read_x_values(tofs_path, skiprows=1, usecols=1, delimiter='\t'),)
    ds.coords["t"] *= 1e3

    # Load tiff stack
    def load_and_scale(folder_name, scale_factor):
        to_load = os.path.join(raw_data_dir, folder_name)
        variable = imaging.tiffs_to_variable(to_load, dtype=np.float32)
        variable *= scale_factor
        return variable

    ds["reference"] = load_and_scale(folder_name="R825-open-beam",
                                     scale_factor=pulse_number_reference)
    ds["sample"] = load_and_scale(folder_name="R825",
                                  scale_factor=pulse_number_sample)
    ds["sample_elastic"] = load_and_scale(folder_name="R825-600-Mpa",
                                          scale_factor=pulse_number_sample_elastic)