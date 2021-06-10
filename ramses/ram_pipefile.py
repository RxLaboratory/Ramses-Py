# -*- coding: utf-8 -*-

import os
from .file_manager import RamFileManager

from .ram_object import RamObject
from .ram_filetype import RamFileType
from .metadata_manager import RamMetaDataManager

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

    def check(self, filePath):
        """Checks if a file corresponds to this pipe.
        Note that the filename must end with the pipe shortname (it must be at the end of its resource)"""

        # It must be of the correct type
        if not self._fileType.check( filePath ):
            return False 

        # Have the type in the metadata
        pipeType = RamMetaDataManager.getPipeType( filePath )
        if pipeType == self.shortName():
            return True
        elif pipeType != '':
            return False

        # Or have the short name in the resource
        fileBlocks = filePath.split('.')[-2]
        if not fileBlocks.endswith(self.shortName()):
            return False
        return True

    def getFiles(self, folderPath):
        """Gets all the files which can enter this pipe from the given folder"""

        if not os.path.isdir(folderPath):
                return []

        files = []

        for file in os.listdir(folderPath):
            filePath = RamFileManager.buildPath((
                folderPath,
                file
            ))
            if self.check( filePath ):
                files.append( filePath )

        return files