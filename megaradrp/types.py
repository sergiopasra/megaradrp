#
# Copyright 2011-2016 Universidad Complutense de Madrid
#
# This file is part of Megara DRP
#
# Megara DRP is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Megara DRP is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Megara DRP.  If not, see <http://www.gnu.org/licenses/>.
#

"""Products of the Megara Pipeline"""

'''
    RAW_BIAS DataFrameType
    RAW_DARK DataFrameType
    RAW_FLAT DataFrameType
    RAW_ILLUM DataFrameType
    RAW_SCIENCE DataFrameType

    MASTER_BIAS  DataFrameType(detector)
    MASTER_DARK  DataFrameType(detector, exposure)
    MASTER_FLAT  DataFrameType(detector, grism)
    MASTER_ILLUM DataFrameType(detector, grism)

    POINTING DataFrameType
    MOSAIC DataFrameType

'''

import uuid

import yaml

import numina.core.types
from numina.array.wavecalib.arccalibration import SolutionArcCalibration
from numina.core import DataFrameType, DataProductType
from numina.core.products import DataProductTag


class MEGARAProductFrame(DataFrameType, DataProductTag):
    pass


# class MEGARAProcessedFrame(DataFrameType):
#     """A processed image not to be stored"""
#     pass


class MasterBias(MEGARAProductFrame):
    pass


class MasterTwilightFlat(MEGARAProductFrame):
    pass

class MasterDark(MEGARAProductFrame):
    pass


class MasterFiberFlat(MEGARAProductFrame):
    pass


class MasterSlitFlat(MEGARAProductFrame):
    pass


class MasterFiberFlatFrame(MEGARAProductFrame):
    pass


class MasterBPM(MEGARAProductFrame):
    pass


class MasterSensitivity(MEGARAProductFrame):
    pass


class MasterWeights(DataProductType):
    def __init__(self, default=None):
        super(MasterWeights, self).__init__(ptype=dict, default=default)

    def _datatype_dump(self, obj, where):
        import shutil

        filename = where.destination + '.tar'

        shutil.copy(obj, filename)
        shutil.rmtree(obj.split(filename)[0])
        return filename

    def _datatype_load(self, obj):
        try:
            import tarfile
            return tarfile.open(obj, 'r')
        except IOError as e:
            raise e


class JSONstorage(DataProductType):
    def __init__(self, default=None):
        super(JSONstorage, self).__init__(ptype=dict, default=default)

    def _datatype_dump(self, obj, where):
        import json
        filename = where.destination + '.json'

        with open(filename, 'w') as fd:
            fd.write(json.dumps(obj, sort_keys=True, indent=2,
                                separators=(',', ': ')))

        return filename

    def _datatype_load(self, obj):
        import json
        try:
            with open(obj, 'r') as fd:
                data = json.load(fd)
        except IOError as e:
            raise e
        return data



class WavelengthCalibration(numina.core.types.AutoDataType):
    def __init__(self, instrument='unknown'):
        super(WavelengthCalibration, self).__init__()

        self.instrument = instrument
        self.tags = {}
        self.uuid = uuid.uuid1().hex
        self.wvlist = {}

    def __getstate__(self):
        st = {}
        st['wvlist'] = {key: val.__getstate__()
                        for (key, val) in self.wvlist.items()}
        for key in ['instrument', 'tags', 'uuid']:
            st[key] = self.__dict__[key]
        return st

    def __setstate__(self, state):
        self.instrument = state['instrument']
        self.tags = state['tags']
        self.uuid = state['uuid']
        self.wvlist = {key: SolutionArcCalibration(**val)
                       for (key, val) in state['wvlist'].items()}
        return self

    @classmethod
    def _datatype_dump(cls, obj, where):
        filename = where.destination + '.yaml'
        import json

        with open(where.destination + '.json', 'w') as fd:
            fd.write(json.dumps(obj.__getstate__(), sort_keys=True, indent=2,
                                separators=(',', ': ')))
        with open(filename, 'w') as fd:
            yaml.dump(obj.__getstate__(), fd)

        return filename

    @classmethod
    def _datatype_load(cls, obj):

        try:
            with open(obj, 'r') as fd:
                state = yaml.load(fd)
        except IOError as e:
            raise e

        result = cls.__new__(cls)
        result.__setstate__(state=state)
        return result

    @property
    def default(self):
        return None


class LCBCalibration(JSONstorage):
    pass