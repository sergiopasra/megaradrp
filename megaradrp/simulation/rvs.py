#
# Copyright 2018 Universidad Complutense de Madrid
#
# This file is part of Megara DRP
#
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSE.txt
#

"""Generate random variates from a given MEGARA image"""


from __future__ import print_function

import uuid

import astropy.io.fits as fits

from megaradrp.simulation.detector import MegaraDetector, ReadParams


def random_variate(fitsfile, size=1):
    """Generate random variates of a given MEGARA image"""

    # First, create a copy
    # copy returns a list instead of a HDUList
    ref = fits.HDUList([hdu.copy() for hdu in fitsfile])
    # Update a few keywords
    primary_header = ref[0].header
    primary_header['DATE'] = 'today'
    baseuuid = primary_header['UUID']
    primary_header['UUIDREF'] = baseuuid
    newuuid = str(uuid.uuid4())
    primary_header['UUID'] = newuuid
    primary_header['HISTORY'] = 'Random variate generated from {}'.format(baseuuid)
    primary_header['ORIGIN'] = 'SIMULATOR'
    # Data section
    # BLCKUUID
    #
    import numpy
    from megaradrp.processing.trimover import OverscanCorrector, TrimImage
    from megaradrp.processing.trimover import GainCorrector
    import megaradrp.loader

    # FIXME: Tooooo complex!
    drp = megaradrp.loader.load_drp()
    ins = drp.configurations['default']

    detconf = ins.get('detector.scan')
    f1 = OverscanCorrector(detconf)
    f2 = TrimImage(detconf)
    f3 = GainCorrector(detconf)

    new = fits.HDUList([hdu.copy() for hdu in fitsfile])
    new = f1(new)
    new = f2(new)
    new = f3(new)

    PSCAN = 50
    DSHAPE = (2056 * 2, 2048 * 2)
    OSCAN = 50

    bias_dw = 2050 + 20
    bias_up = 2050 - 20

    dark = 0.0  # In 1 hour
    exptime = primary_header['EXPTIME']
    dark_s = dark / exptime
    qe = 1

    # This is wrong in the header
    gain_dw = 1.73 # Bottom e-/ADU
    gain2 = 1.6 # Top e-/ADU
    ron_dw = 3.4 # Bottom
    ron2 = 3.4 # Top


    # RON here must be in ADU, not in e-
    readpars_dw = ReadParams(gain=gain_dw, ron=ron_dw, bias=bias_dw)
    readpars_up = ReadParams(gain=gain2, ron=ron2, bias=bias_up)

    detector = MegaraDetector(
        'megara_model_detector',
        DSHAPE, OSCAN, PSCAN,
        qe=qe, dark=dark_s,
        readpars1=readpars_up,
        readpars2=readpars_dw,
        bins='11'
    )

    elec_mean = numpy.abs(new[0].data / exptime)

    new.writeto('/tmp/new.fits', overwrite=True)
    # FIXME: hardcoded
    for idx in range(size):
        newop = fits.HDUList([hdu.copy() for hdu in ref])
        detector.expose(elec_mean, time=exptime)
        newdata = detector.readout()
        newop[0].data = numpy.flipud(newdata)

        newop[0].header['DATE'] = 'today'
        newop[0].header['UUID'] = str(uuid.uuid4())
        yield newop
