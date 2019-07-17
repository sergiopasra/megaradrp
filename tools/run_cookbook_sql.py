
import os
import pathlib
import logging
import tarfile
import yaml

import numina.util.context as ctx
from numina.dal.sqldal import SqliteDAL
from numina.dal.db.base import Base
from numina.user.helpers import load_observations, DataManager,parse_as_yaml
from numina.user.baserun import run_reduce
from numina.tests.testcache import download_cache


def create_datamanager(dal, basedir, datadir,
                       extra_control=None, profile_path_extra=None
                       ):

    if extra_control:
        loaded_data_extra = parse_as_yaml(extra_control)
    else:
        loaded_data_extra = None

    _backend = dal
    datamanager = DataManager(basedir, datadir, _backend)

    return datamanager

def main():

    logging.basicConfig(level=logging.DEBUG)

    basedir = pathlib.Path().resolve()

    tarball = 'MEGARA-cookbook-M15_LCB_HR-R-v1.tar.gz'
    url = 'http://guaix.fis.ucm.es/~spr/megara_test/{}'.format(tarball)

    # downloaded = download_cache(url)

    # Uncompress
    # with tarfile.open(downloaded.name, mode="r:gz") as tar:
    with tarfile.open(tarball, mode="r:gz") as tar:
        tar.extractall()

    # os.remove(downloaded.name)

    persist = False

    datadir = basedir / 'data'

    dialect = None

    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker()
    db_uri = 'sqlite:///processing.db'
    engine = create_engine(db_uri, echo=False)

    Base.metadata.create_all(bind=engine)

    Session.configure(bind=engine)
    session = Session()

    sqldal = SqliteDAL(dialect, session, basedir, datadir)

    dm = create_datamanager(sqldal, basedir, datadir)

    if not persist:
        with ctx.working_directory(basedir):
            obsresults = ["0_bias.yaml", "2_M15_modelmap.yaml",
         "4_M15_fiberflat.yaml", "6_M15_Lcbadquisition.yaml",
         "8_M15_reduce_LCB.yaml", "1_M15_tracemap.yaml",
         "3_M15_wavecalib.yaml", "5_M15_twilight.yaml",
         "7_M15_Standardstar.yaml"]

            #obsresults = ["0_bias.yaml", "1_M15_tracemap.yaml"]

            #sessions, loaded_obs = load_observations(obsresults, is_session=False)
            #dm.backend.add_obs(loaded_obs)
    try:
        if not persist:
            obsid = "0_bias"
            task0 = run_reduce(dm, obsid)
            #return 0
            obsid = "1_HR-R"
            task1 = run_reduce(dm, obsid)
            return 0
            obsid = "3_HR-R"
            task3 = run_reduce(dm, obsid)

            obsid = "4_HR-R"
            task4 = run_reduce(dm, obsid)

            obsid = "5_HR-R"
            task5 = run_reduce(dm, obsid)

            obsid = "6_HR-R"
            task6 = run_reduce(dm, obsid)

            obsid = "7_HR-R"
            task7 = run_reduce(dm, obsid)

            obsid = "8_HR-R"
            task8 = run_reduce(dm, obsid)

    finally:
        with ctx.working_directory(basedir):
            with open('control_dump.yaml', 'w') as fd:
                datam = dm.backend.dump_data()
                yaml.dump(datam, fd)


if __name__ == '__main__':

    main()
