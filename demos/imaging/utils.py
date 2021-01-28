import os
import sys

import ess.v20.imaging as imaging
import ess.v20.imaging.operations as operations
import ess.wfm as wfm

import dataconfig
import scipp as sc
import numpy as np

from scipy import ndimage, signal

local_data_path = os.path.join('ess', 'v20', 'imaging',
                               'gp2-stress-experiments')
data_dir = os.path.join(dataconfig.data_root, local_data_path)
output_dir = os.path.join(dataconfig.data_root, 'output')
instrument_file = os.path.join(data_dir, 'V20_Definition_GP2.xml')

tofs_path = os.path.join(data_dir, 'GP2_Stress_time_values.txt')
raw_data_dir = os.path.join(data_dir)

if not os.path.exists(data_dir):
    raise FileNotFoundError("The following data directory does not exist,"
                            f" check your make_config.py:\n{data_dir}")


def to_bin_centers(x, dim):
    """
    Convert array edges to centers
    """
    return 0.5 * (x[dim, 1:] + x[dim, :-1])


def to_bin_edges(x, dim):
    """
    Convert array centers to edges
    """
    idim = x.dims.index(dim)
    if x.shape[idim] < 2:
        one = 1.0 * x.unit
        return sc.concatenate(x[dim, 0:1] - one, x[dim, 0:1] + one, dim)
    else:
        center = to_bin_centers(x, dim)
        # Note: use range of 0:1 to keep dimension dim in the slice to avoid
        # switching round dimension order in concatenate step.
        left = center[dim, 0:1] - (x[dim, 1] - x[dim, 0])
        right = center[dim, -1] + (x[dim, -1] - x[dim, -2])
        return sc.concatenate(sc.concatenate(left, center, dim), right, dim)


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
    ds.coords["t"] = sc.Variable(
        ["t"],
        unit=sc.units.us,
        values=imaging.read_x_values(tofs_path,
                                     skiprows=1,
                                     usecols=1,
                                     delimiter='\t'),
    )
    ds.coords["t"] *= 1e3

    ds["reference"] = load_and_scale(folder_name="R825-open-beam",
                                     scale_factor=pulse_number_reference)
    ds["sample"] = load_and_scale(folder_name="R825",
                                  scale_factor=pulse_number_sample)
    ds["sample_elastic"] = load_and_scale(
        folder_name="R825-600-Mpa", scale_factor=pulse_number_sample_elastic)

    # Geometry
    geometry = sc.Dataset()
    sc.compat.mantid.load_component_info(geometry, instrument_file)
    geom = sc.Dataset(
        coords={
            # "sample-position": geometry.coords["sample-position"],
            "source-position": geometry.coords["source-position"]
        })
    geom.coords["position"] = sc.reshape(geometry.coords['position'],
                                         dims=['y', 'x'],
                                         shape=tuple(ds["sample"]["t",
                                                                  0].shape))
    geom.coords["x"] = to_bin_edges(
        sc.geometry.x(geom.coords["position"])["y", 0], "x")
    geom.coords["y"] = to_bin_edges(
        sc.geometry.y(geom.coords["position"])["x", 0], "y")
    ds = sc.merge(ds, geom)
    ds

    return ds


def create_Braggedge_list(lattice_constant, miller_indices):
    '''
    :param miller-indices: like [(1,1,0),(2,0,0),...]
    :type miller-indices: list of tuples
    '''
    coords = [str((h, k, l)) for h, k, l in miller_indices]
    interplanar_distances = [
        2. * lattice_constant / np.sqrt(h**2 + k**2 + l**2)
        for h, k, l in miller_indices
    ]

    d = sc.DataArray(
        sc.Variable(dims=["bragg-edge"],
                    values=np.array(interplanar_distances),
                    unit=sc.units.angstrom))
    d.coords["miller-indices"] = sc.Variable(dims=["bragg-edge"],
                                             values=coords)
    return d


def groupby2D(data, nbins):

    dim_to_shape = dict(zip(data.dims, data.shape))
    #     [n_wav, ny_original, nx_original] = data.shape
    nx_target = nbins
    ny_target = nbins

    element_width_x = dim_to_shape['x'] // nx_target
    element_width_y = dim_to_shape['y'] // ny_target

    x = sc.Variable(dims=['x'],
                    values=np.arange(dim_to_shape['x']) // element_width_x)
    y = sc.Variable(dims=['y'],
                    values=np.arange(dim_to_shape['y']) // element_width_y)
    grid = x + nx_target * y
    spectrum_mapping = sc.Variable(["spectrum"],
                                   values=np.ravel(grid.values, order='F'))

    reshaped = sc.Dataset()
    for key in data:
        item = sc.DataArray(data=sc.reshape(data[key].data,
                                            dims=["wavelength", "spectrum"],
                                            shape=(dim_to_shape['wavelength'],
                                                   dim_to_shape['x'] *
                                                   dim_to_shape['y'])))
        item.coords["spectrum"] = sc.array(dims=["spectrum"],
                                           values=np.arange(dim_to_shape['x'] *
                                                            dim_to_shape['y']))
        for c in ["wavelength", "source-position"]:
            item.coords[c] = data[key].coords[c]
        for m in data[key].masks:
            item.masks[m] = sc.reshape(data[key].masks[m],
                                       dims=["spectrum"],
                                       shape=(dim_to_shape['x'] *
                                              dim_to_shape['y'], ))
        reshaped[key] = item
    reshaped

    reshaped.coords["spectrum_mapping"] = spectrum_mapping

    grouped = sc.groupby(reshaped,
                         "spectrum_mapping").sum("spectrum")  # try "mean"

    reshaped = sc.Dataset()
    for key in grouped:
        item = sc.DataArray(data=sc.reshape(grouped[key].data,
                                            dims=["wavelength", "y", "x"],
                                            shape=(dim_to_shape['wavelength'],
                                                   ny_target, nx_target)))

        item.coords["x"] = sc.array(dims=["x"],
                                    values=np.linspace(
                                        data.coords['x']['x', 0].value,
                                        data.coords['x']['x',
                                                         -1].value, nbins + 1),
                                    unit=data.coords['x'].unit)
        item.coords["y"] = sc.array(dims=["y"],
                                    values=np.linspace(
                                        data.coords['y']['y', 0].value,
                                        data.coords['y']['y',
                                                         -1].value, nbins + 1),
                                    unit=data.coords['y'].unit)
        for c in ["wavelength", "source-position"]:
            item.coords[c] = data[key].coords[c]
        for m in grouped[key].masks:
            item.masks[m] = sc.reshape(grouped[key].masks[m],
                                       dims=["y", "x"],
                                       shape=(
                                           ny_target,
                                           nx_target,
                                       ))
        reshaped[key] = item
    return reshaped


def fit(Bragg_edges_FCC, reference):

    x_min_sides = [0.05, 0.1, 0.1, 0.05]  #[0.1, 0.1, 0.1, 0.05]
    x_max_sides = [0.1, 0.05, 0.1, 0.1]  #[0.1, 0.1, 0.1, 0.1]
    fit_list = []
    spectrum_list_fitted_sample = []
    spectrum_list_fitted_sample_elastic = []
    #     elastic_ws = grouped_sample_elastic
    #     sample_ws = sample_final

    for edge_index in range(Bragg_edges_FCC.shape[0]):
        #         fit_list.append([])
        spectrum_list_fitted_sample.append([])
        spectrum_list_fitted_sample_elastic.append([])

        bragg_edge = Bragg_edges_FCC.coords["miller-indices"]["bragg-edge",
                                                              edge_index]

        xpos_guess = Bragg_edges_FCC["bragg-edge", edge_index].value
        x_min_fit = xpos_guess - xpos_guess * abs(x_min_sides[edge_index])
        x_max_fit = xpos_guess + xpos_guess * abs(x_max_sides[edge_index])

        print(
            "Now fitting Bragg edge {} at {:.3f} A (between {:.3f} A and {:.3f} A) across image groups"
            .format(bragg_edge, xpos_guess, x_min_fit, x_max_fit))

        # if the full inital sample was taken and no grouping was done
        #Fitting the masked sample
        params_s, diff_s = sc.compat.mantid.fit(
            reference,
            mantid_args={
                'Function':
                f'name=LinearBackground,A0={270},A1={-10};name=UserFunction,Formula=h*erf(a*(x-x0)),h={200},a={-11},x0={xpos_guess}',
                'StartX': x_min_fit,
                'EndX': x_max_fit
            })

        v_and_var_s = [
            params_s.data['parameter', i]
            for i in range(params_s['parameter', :].shape[0])
        ]
        params = dict(zip(params_s.coords["parameter"].values, v_and_var_s))
        #         fit_list.append({"params": params_s, "diff": diff_s})
        fit_list.append(params)
        d_sample = params[
            "f1.x0"] / 2.0  # See fit table definition for extract x0
        # print(edge_index, bragg_edge, d_sample.value, d_sample.value * 2.0)
    return fit_list
