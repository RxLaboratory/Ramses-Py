# -*- coding: utf-8 -*-

#====================== BEGIN GPL LICENSE BLOCK ======================
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 3
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#======================= END GPL LICENSE BLOCK ========================

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
            pipeFileDict['colorSpace'],
            pipeFileDict['customSettings']
        )

    def __init__(self, shortName, fileType, colorSpace = '', customSettings = ''):
        super(RamPipeFile, self).__init__( '', shortName )
        self._fileType = fileType
        self._colorSpace = colorSpace
        self._customSettings = customSettings

    def fileType(self):
        return self._fileType

    def colorSapce(self):
        return self._colorSpace

    def customSettings(self):
        return self._customSettings

    def check(self, filePath, checkFileType=False):
        """Checks if a file corresponds to this pipe.
        Note that the filename must end with the pipe shortname (it must be at the end of its resource)"""

        # It must be of the correct type
        if not self._fileType.check( filePath ) and checkFileType:
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
    