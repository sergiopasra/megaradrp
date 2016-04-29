from __future__ import print_function

import os
import logging
import datetime

import numpy as np
from astropy import units as u
from astropy.io import fits

from megaradrp.simulation.instrument import MegaraInstrument
from megaradrp.simulation.efficiency import EfficiencyFile
from megaradrp.simulation.efficiency import InterpolFile
from megaradrp.simulation.instrument import InternalOptics
from megaradrp.simulation.wheel import VPHWheel
from megaradrp.simulation import lamps
from megaradrp.simulation import calibrationunit
from megaradrp.simulation.actions import megara_sequences
from megaradrp.simulation.telescope import Telescope
from megaradrp.simulation.fiberbundle import FiberBundle
from megaradrp.simulation.instrument import PseudoSlit
from megaradrp.simulation.focalplane import FocalPlane
from megaradrp.simulation.detector import ReadParams, MegaraDetectorSat
from megaradrp.simulation.vph import MegaraVPH
from megaradrp.simulation.shutter import MegaraShutter

_logger = logging.getLogger("megaradrp.simulation")


# create detector from data
def create_detector():
    _logger.info('create detector')
    DSHAPE = (2056 * 2, 2048 * 2)
    PSCAN = 50
    OSCAN = 50
    #qe = 1.0 * np.ones(DSHAPE)
    qe = fits.getdata('v02/base_qe.fits')
    dcurrent = 3.0 / 3600

    readpars1 = ReadParams(gain=1.0, ron=2.0, bias=1000.0)
    readpars2 = ReadParams(gain=1.0, ron=2.0, bias=1005.0)

    qe_wl = EfficiencyFile('v02/tccdbroad_0.1aa.dat')

    detector = MegaraDetectorSat('megaradetector',
                                 DSHAPE, OSCAN, PSCAN, qe=qe, qe_wl=qe_wl, dark=dcurrent,
                                 readpars1=readpars1, readpars2=readpars2, bins='11'
                                 )
    return detector


def create_lcb(focal_plane):
    _logger.info('create lcb')
    layouttable = np.loadtxt('v02/LCB_spaxel_centers.dat')
    fib_ids = layouttable[:,4].astype('int').tolist()
    bun_ids = layouttable[:,3].astype('int').tolist()

    trans = EfficiencyFile('v02/tfiber_0.1aa_20m.dat')
    fibers_lcb = FiberBundle("BUNDLE.LCB", fib_ids, bun_ids, static=True, transmission=trans, inactive=[1, 3])

    pseudo_slit_lcb = PseudoSlit(name="PSLT.LCB", insmode='LCB')
    pseudo_slit_lcb.connect_fibers(fib_ids, layouttable[:,2])

    focal_plane.connect_fiber_bundle(fibers_lcb, fib_ids, layouttable[:,0:2])
    return focal_plane, fibers_lcb, pseudo_slit_lcb


def create_mos(focal_plane):
    _logger.info('create mos')
    layouttable = np.loadtxt('v02/MOS_spaxel_centers.dat')
    fib_ids = layouttable[:,4].astype('int').tolist()
    bun_ids = layouttable[:,3].astype('int').tolist()
    trans = EfficiencyFile('v02/tfiber_0.1aa_20m.dat')
    fibers_mos = FiberBundle("BUNDLE.MOS", fib_ids, bun_ids, static=False, transmission=trans, inactive=[1, 3])

    pseudo_slit_mos = PseudoSlit(name="PSLT.MOS", insmode='MOS')
    pseudo_slit_mos.connect_fibers(fib_ids, layouttable[:,2])

    focal_plane.connect_fiber_bundle(fibers_mos, fib_ids, layouttable[:,0:2])
    return focal_plane, fibers_mos, pseudo_slit_mos


def create_wheel():
    _logger.info('create wheel')
    wheel = VPHWheel(capacity=3, name='wheel')
    _logger.info('create vphs')
    vph = create_vph_by_data('VPH405_LR',
                              'v02/VPH405_LR2-extra.dat',
                              'v02/VPH405_LR_res.dat',
                              'v02/tvph_0.1aa.dat'
                             )
    wheel.put_in_pos(vph, 0)
    vph = create_vph_by_data('VPH926_MR',
                              'v02/VPH926_MR.txt',
                              'v02/VPH926_MR_res.dat',
                              'v02/tvph_0.1aa.dat'
                         )
    wheel.put_in_pos(vph, 1)
    vph = create_vph_by_data('VPH863_HR',
                             'v02/VPH863_HR.txt',
                             'v02/VPH863_HR_res.dat',
                              'v02/tvph_0.1aa.dat'
                         )
    wheel.put_in_pos(vph, 2)
    return wheel


def create_vph_by_data(name, distortion, resolution, transmission):
    trans = EfficiencyFile(transmission)
    res = EfficiencyFile(resolution)
    vph = MegaraVPH(name=name, vphtable=distortion,
                    resolution=res,
                    transmission=trans)

    return vph


def create_optics():
    _logger.info('create internal optics')
    t = EfficiencyFile('v02/tspect_0.1aa.dat')
    i = InternalOptics(transmission=t)
    return i


def illum1(x, y):
    """Explicit illumination in the focal plane"""
    r = np.hypot(x, y)
    return np.where(r <= 50.0, 1.0, 0.5)


def illum2(x, y):
    """Explicit illumination in the focal plane"""
    r = np.hypot(x, y)
    return 1.0 / (1 + np.exp((r - 130.0) / 10.0))


def create_instrument():
    # eq = np.random.normal(loc=0.80, scale=0.01, size=(4096,4096))
    # eq = np.clip(eq, 0.0, 1.0)
    # fits.writeto('eq.fits', eq, clobber=True)
    # eq = fits.getdata('eq.fits')

    # Assemble instrument

    detector = create_detector()

    focal_plane = FocalPlane()
    focal_plane, fibers_lcb, pseudo_slit_lcb = create_lcb(focal_plane)
    focal_plane, fibers_mos, pseudo_slit_mos = create_mos(focal_plane)

    pseudo_slit = dict(lcb=pseudo_slit_lcb, mos=pseudo_slit_mos)
    fibers = dict(lcb=fibers_lcb, mos=fibers_mos)

    wheel = create_wheel()
    internal = create_optics()
    _logger.info('create instrument')
    instrument = MegaraInstrument(focal_plane=focal_plane,
                                  fibers=fibers,
                                  wheel=wheel,
                                  pseudo_slit=pseudo_slit,
                                  internal_optics=internal,
                                  detector=detector,
                                  shutter=MegaraShutter()
    )
    return instrument


def create_calibration_unit(illum=None):

    cu = calibrationunit.MegaraCalibrationUnit(capacity=7, name='megcalib')

    lamp1 = lamps.BlackBodyLamp('FLAT1', 5400 * u.K, illumination=illum)
    lamp2 = lamps.FlatLamp('FLAT2', photons=7598.34893859, illumination=illum)
    lamp3 = lamps.ArcLamp('ARC', illumination=illum)
    lamp4 = lamps.BlackBodyLamp('HALO1', 5400 * u.K, illumination=illum)
    lamp5 = lamps.FlatLamp('HALO2', photons=7598.34893859, illumination=illum)
    lamp6 = lamps.ArcLamp('ARC1', illumination=illum)

    cu.put_in_pos('EMPTY', 0)
    cu.put_in_pos(lamp1, 1)
    cu.put_in_pos(lamp2, 2)
    cu.put_in_pos(lamp3, 3)
    cu.put_in_pos(lamp4, 4)
    cu.put_in_pos(lamp5, 5)
    cu.put_in_pos(lamp6, 6)

    return cu


def create_telescope():

    tel = Telescope(name='GTC', diameter=100.0, transmission=EfficiencyFile('v02/ttel_0.1aa.dat'))

    return tel


def restricted_float(x):
    x = float(x)
    if x < 0.0 or x > 36000.0:
        raise argparse.ArgumentTypeError("%r not in range [0.0, 36000.0]" % (x,))
    return x


if __name__ == '__main__':

    import yaml
    import argparse

    from megaradrp.simulation.factory import MegaraImageFactory
    from megaradrp.simulation.atmosphere import AtmosphereModel

    try:
        from numinadb.controldb import ControlSystem
    except ImportError:
        from megaradrp.simulation.control import ControlSystem

    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser(prog='megara_sim_b')

    parser.add_argument('-p', '--parameters', metavar="FILE",
                        help="FILE with observing parameters")
    parser.add_argument('-t', '--targets', metavar="FILE",
                        help="FILE with target configuration")
    parser.add_argument('-e', '--exposure', type=restricted_float, default=0.0,
                        help="Exposure time per image (in seconds) [0,36000]")
    parser.add_argument('-n', '--nimages', metavar="INT", type=int, default=1,
                        help="Number of images to generate")

    parser.add_argument('omode', choices=megara_sequences().keys(),
                        help="Observing mode of the intrument")

    args = parser.parse_args()

    illum = None
    cu = create_calibration_unit(illum=None)
    instrument = create_instrument()
    telescope = create_telescope()
    atm = AtmosphereModel(twilight=InterpolFile('v02/sky/tw-spec.txt'),
                          nightsky=InterpolFile('v02/sky/uves_sky_phot.txt')
                          )
    telescope.connect(atm)
    factory = MegaraImageFactory()

    control = ControlSystem(factory)
    control.register('MEGARA', instrument)
    control.register('GTC', telescope)
    control.register('megcalib', cu)
    control.register('factory', factory)

    # Observation setup

    if args.parameters:

        oparam = yaml.load(open(args.parameters))

        _logger.debug('Configure MEGARA with profile %s', oparam['description'])
        instrument.configure(oparam)

        cu.select(oparam['lamp'])

    if args.targets:
        _logger.debug('load targets file %s', args.targets)
        targets = yaml.load(open(args.targets))
    else:
        # empty target list
        targets = dict(central=[0.0, 0.0], targets=dict())

    control.set_targets(targets)

    _logger.info('start simulation')
    control.set_mode(args.omode)

    etime = args.exposure
    repeat = args.nimages

    _logger.debug('Exposure time is %f', etime)
    _logger.debug('Number of images is %d', repeat)
    with control:
        control.run(exposure=etime, repeat=repeat)