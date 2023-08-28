
import os
import pathlib
import logging
import tarfile
import yaml

import numina.util.context as ctx
from numina.user.helpers import create_datamanager, load_observations
from numina.user.baserun import run_reduce
from numina.tests.testcache import download_cache


def main():

    logging.basicConfig(level=logging.DEBUG)

    basedir = pathlib.Path().resolve()

    tarball = 'MEGARA-cookbook-M15_LCB_HR-R-v1.tar.gz'
    url = 'http://guaix.fis.ucm.es/~spr/megara_test/{}'.format(tarball)

    # downloaded = download_cache(url)

    # Uncompress
    # with tarfile.open(downloaded.name, mode="r:gz") as tar:
    #with tarfile.open(tarball, mode="r:gz") as tar:
    #    tar.extractall()

    # os.remove(downloaded.name)

    persist = False

    if persist:
        reqfile = basedir / 'control_dump.yaml'
    else:
        reqfile = basedir / 'control_v2.yaml'

    datadir = basedir / 'data'

    dm = create_datamanager(reqfile, basedir, datadir)

    if not persist:
        with ctx.working_directory(basedir):
            obsresults = ["0_bias.yaml", "2_M15_modelmap.yaml",
         "4_M15_fiberflat.yaml", "6_M15_Lcbadquisition.yaml",
         "8_M15_reduce_LCB.yaml", "1_M15_tracemap.yaml",
         "3_M15_wavecalib.yaml", "5_M15_twilight.yaml",
         "7_M15_Standardstar.yaml"]

            sessions, loaded_obs = load_observations(obsresults, is_session=False)
            dm.backend.add_obs(loaded_obs)

    try:
        if not persist:
            obsid = "0_bias"
            task0 = run_reduce(dm, obsid, validate_inputs=True, validate_results=True)

            obsid = "1_HR-R"
            task1 = run_reduce(dm, obsid, validate_inputs=True, validate_results=True)

            obsid = "3_HR-R"
            task3 = run_reduce(dm, obsid, validate_inputs=True, validate_results=True)

            obsid = "4_HR-R"
            task4 = run_reduce(dm, obsid, validate_inputs=True, validate_results=True)

            obsid = "5_HR-R"
            task5 = run_reduce(dm, obsid, validate_inputs=True, validate_results=True)

            obsid = "6_HR-R"
            task6 = run_reduce(dm, obsid, validate_inputs=True, validate_results=True)

            obsid = "7_HR-R"
            task7 = run_reduce(dm, obsid, validate_inputs=True, validate_results=True)

            obsid = "8_HR-R"
            task8 = run_reduce(dm, obsid, validate_inputs=True, validate_results=True)
    finally:
        with ctx.working_directory(basedir):
            with open('control_dump.yaml', 'w') as fd:
                datam = dm.backend.dump_data()
                yaml.dump(datam, fd)


if __name__ == '__main__':

    main()
