def q1d(data, transmission, l_collimation, r1, r2, dr, wavelength_bands=None):
    transmission = setup_transmission(transmission)
    data = data.copy()
    apply_masks(data)
    data = sc.neutron.convert(data, 'tof', 'wavelength', out=data)
    data = sc.rebin(data, 'wavelength', wavelength_bins)

    monitor = data.meta['monitor1'].value
    monitor = background_mean(monitor, 'tof', 40000.0 * sc.units.us,
                              99000.0 * sc.units.us)
    monitor = sc.neutron.convert(monitor, 'tof', 'wavelength', out=monitor)
    monitor = sc.rebin(monitor, 'wavelength', wavelength_bins)

    # this factor seems to be a fudge factor. Explanation pending.
    data *= 100.0 / 176.71458676442586

    # Setup direct beam and normalise to monitor. I.e. adjust for efficiency of detector across the wavelengths.
    direct_beam = load_rkh(filename=f'{path}/{direct_beam_file}')
    # This would work assuming that there is a least one wavelength point per bin
    #direct_beam = sc.groupby(direct_beam, 'wavelength', bins=monitor.coords['wavelength']).mean('wavelength')
    direct_beam = map_to_bins(direct_beam, 'wavelength',
                              monitor.coords['wavelength'])
    direct_beam = monitor * transmission * direct_beam

    # Estimate qresolution function
    moderator = load_rkh(filename=f'{path}/{moderator_file}')
    to_bin_edges(moderator, 'wavelength')

    q_bins = sc.Variable(dims=['Q'],
                         unit=sc.units.one / sc.units.angstrom,
                         values=np.geomspace(0.008, 0.6, num=55))

    d = sc.Dataset({'data': data, 'norm': solid_angle(data) * direct_beam})

    if wavelength_bands is None:

        #dq_sq = q_resolution(_d.coords['wavelength'], moderator, d, l_collimation, r1, r2, dr)
        to_bin_centers(d, 'wavelength')
        d = sc.neutron.convert(d, 'wavelength', 'Q',
                               out=d)  # TODO no gravity yet

        d = sc.histogram(d, q_bins)
        d = sc.sum(d, 'spectrum')
        I = d['data'] / d['norm']
    else:

        # Reduce by wavelength slice
        n_band = int(wavelength_bands)
        high = sc.nanmax(wavelength_bins)
        low = sc.nanmin(wavelength_bins)
        step = (high.value - low.value) / n_band
        range_edges = np.arange(low.value, high.value + step, step)
        slices = [
            slice(sc.Variable(value=i, unit=sc.units.angstrom),
                  sc.Variable(value=j, unit=sc.units.angstrom))
            for i, j in zip(range_edges[:-1:], range_edges[1::])
        ]
        bands = None
        for slc in slices:
            _d = d['wavelength', slc].copy()
            to_bin_centers(_d, 'wavelength')
            _d = sc.neutron.convert(_d, 'wavelength', 'Q',
                                    out=_d)  # TODO no gravity yet
            #dq_sq = q_resolution(_d.coords['wavelength'], moderator, d, l_collimation, r1, r2, dr)
            band = sc.histogram(
                _d, q_bins)  # TODO fix scipp to avoid need for copy
            band = sc.sum(band, 'spectrum')
            bands = sc.concatenate(bands, band,
                                   'wavelength') if bands is not None else band
        bands.coords['wavelength'] = sc.Variable(['wavelength'],
                                                 values=range_edges,
                                                 unit=sc.units.angstrom)
        I = bands['data'] / bands['norm']

    return I
