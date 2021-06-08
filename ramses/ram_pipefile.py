# -*- coding: utf-8 -*-

from .ram_object import RamObject
from .ram_filetype import RamFileType

class RamPipeFile( RamObject ):
    """A file which goes through a RamPipe."""

    @staticmethod
    def fromDict( pipeFileDict ):
        fileType = RamFileType.fromDict( pipeFileDict['fileType'])

        return RamPipeFile(
            pipeFileDict['shortName'],
            fileType,
            pipeFileDict['colorSpace']
        )

    def __init__(self, shortName, fileType, colorSpace = ''):
        super(RamPipeFile, self).__init__( '', shortName )
        self._fileType = fileType
        self._colorSpace = colorSpace

    def fileType(self):
        return self._fileType

    def colorSapce(self):
        return self._colorSpace