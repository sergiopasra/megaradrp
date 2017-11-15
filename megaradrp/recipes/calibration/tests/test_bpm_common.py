#
# Copyright 2015-2017 Universidad Complutense de Madrid
#
# This file is part of Megara DRP
#
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSE.txt
#

"""Tests for the bpm mode recipe module."""

import astropy.io.fits as fits
import numpy as np
from numina.core import DataFrame, ObservationResult

from megaradrp.instrument.loader import build_instrument_config, Loader

def generate_bias(detector, number, temporary_path):
    from megaradrp.simulation.actions import simulate_bias
    from megaradrp.recipes.calibration.bias import BiasRecipe

    config_uuid = '4fd05b24-2ed9-457b-b563-a3c618bb1d4c'
    fs = [simulate_bias(detector) for i in range(number)]
    header = fits.Header()
    header['DATE-OBS'] = '2017-11-09T11:00:00.0'
    for aux in range(len(fs)):
        fits.writeto('%s/bias_%s.fits' % (temporary_path, aux), fs[aux],
                     header=header,
                     clobber=True)

    fs = ["%s/bias_%s.fits" % (temporary_path, i) for i in range(number)]

    ob = ObservationResult()
    ob.instrument = 'MEGARA'
    ob.mode = 'bias_image'
    ob.configuration = build_instrument_config(config_uuid, loader=Loader())
    ob.frames = [DataFrame(filename=f) for f in fs]

    recipe = BiasRecipe()
    ri = recipe.create_input(obresult=ob)
    return recipe.run(ri)


def crear_archivos(temporary_path, number=5):
    from megaradrp.simulation.actions import simulate_flat
    from megaradrp.simulation.detector import ReadParams, MegaraDetectorSat
    from megaradrp.recipes.calibration.bpm import BadPixelsMaskRecipe

    config_uuid = '4fd05b24-2ed9-457b-b563-a3c618bb1d4c'
    PSCAN = 50
    DSHAPE = (2056 * 2, 2048 * 2)
    OSCAN = 50
    ron = 2.0
    gain = 1.0
    bias = 1000.0

    qe = 0.8 * np.ones(DSHAPE)
    qe[0:15, 0:170] = 0.0

    readpars1 = ReadParams(gain=gain, ron=ron, bias=bias)
    readpars2 = ReadParams(gain=gain, ron=ron, bias=bias)

    detector = MegaraDetectorSat('megara_test_detector', DSHAPE, OSCAN, PSCAN,
                                 qe=qe,
                                 dark=(3.0 / 3600.0),
                                 readpars1=readpars1, readpars2=readpars2,
                                 bins='11')

    source2 = 1.0

    fs = [simulate_flat(detector, exposure=1.0, source=5000 * source2) for i in
          range(number)]

    header = fits.Header()
    header['DATE-OBS'] = '2017-11-09T11:00:00.0'
    for aux in range(len(fs)):
        fits.writeto('%s/flat_%s.fits' % (temporary_path, aux), fs[aux],
                     header=header,
                     clobber=True)

    result = generate_bias(detector, number, temporary_path)
    result.master_bias.frame.writeto(
        '%s/master_bias_data0.fits' % temporary_path,
        clobber=True)  # Master Bias

    ob = ObservationResult()
    ob.instrument = 'MEGARA'
    ob.mode = 'bias_image'
    ob.configuration = build_instrument_config(config_uuid, loader=Loader())

    names = []
    for aux in range(number):
        names.append('%s/flat_%s.fits' % (temporary_path, aux))
    ob.frames = [DataFrame(filename=open(nombre).name) for nombre in names]

    recipe = BadPixelsMaskRecipe()
    ri = recipe.create_input(obresult=ob, master_bias=DataFrame(
        filename=open(temporary_path + '/master_bias_data0.fits').name))
    aux = recipe.run(ri)
    aux.master_bpm.frame.writeto('%s/master_bpm.fits' % temporary_path, clobber=True)

    return names
