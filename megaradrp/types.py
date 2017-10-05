#
# Copyright 2011-2017 Universidad Complutense de Madrid
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


from numina.core import DataFrameType, DataProductType
from numina.core.types import DataType
from numina.core.products import convert_date
from numina.core.products import DataProductTag, ArrayType

from .processing.datamodel import MegaraDataModel


class MegaraFrame(DataFrameType):
    """A processed frame"""

    tags_headers = {}

    def __init__(self):
        super(MegaraFrame, self).__init__(datamodel=MegaraDataModel())


class ProcessedFrame(MegaraFrame):
    """A processed frame"""

    tags_headers = {}


class ProcessedImage(ProcessedFrame):
    """A processed image"""
    pass


class ProcessedRSS(ProcessedFrame):
    """A processed RSS image"""
    pass


class ProcessedMultiRSS(ProcessedFrame):
    """A processed RSS image not to be stored"""
    pass


class ProcessedSpectrum(ProcessedFrame):
    """A 1d spectrum"""
    pass


class ProcessedImageProduct(DataProductTag, ProcessedImage):
    pass


class ProcessedRSSProduct(DataProductTag, ProcessedRSS):
    pass


class ProcessedSpectrumProduct(DataProductTag, ProcessedSpectrum):
    pass

class MasterBias(ProcessedImageProduct):
    """A Master Bias image"""
    pass


class MasterTwilightFlat(ProcessedRSSProduct):
    pass


class MasterDark(ProcessedImageProduct):
    """A Master Dark image"""
    pass


class MasterFiberFlat(ProcessedRSSProduct):
    tags_headers = {'insmode': 'insmode', 'vph': 'vph'}


class MasterSlitFlat(ProcessedImageProduct):
    tags_headers = {'insmode': 'insmode', 'vph': 'vph'}


class MasterFiberFlatFrame(ProcessedRSSProduct):
    tags_headers = {
        'insmode': 'insmode',
        'vph': 'vph',
        'confid': ('confid', 'FIBERS', lambda x: x)
    }


class MasterBPM(ProcessedImageProduct):
    """Bad Pixel Mask product"""
    pass


class MasterSensitivity(ProcessedSpectrumProduct):
    """Sensitivity correction."""
    pass


class ReferenceExtinctionTable(DataProductTag, ArrayType):
    """Atmospheric Extinction."""
    pass


class ReferenceSpectrumTable(DataProductTag, ArrayType):
    """The spectrum of a reference star"""
    pass


class WeightsMap(DataProductType):
    def __init__(self, default=None):
        super(WeightsMap, self).__init__(ptype=dict, default=default)

    def _datatype_dump(self, obj, where):
        import shutil

        filename = where.destination + '.tar'

        shutil.copy(obj, filename)
        return filename

    def _datatype_load(self, obj):
        try:
            import tarfile
            return tarfile.open(obj, 'r')
        except IOError as e:
            raise e


class JSONstorage(DataType):
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


class FocusWavelength(JSONstorage):
    """Rich table with focus and wavelength"""
    pass
