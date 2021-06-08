# -*- coding: utf-8 -*-

import os

from .ram_object import RamObject

class RamFileType( RamObject ):
    """A File type.
    File types are typically used with RamPipe."""

    @staticmethod
    def fromDict( fileTypeDict ):
        """Builds a RamFileType from dict like the ones returned by the RamDaemonInterface"""

        return RamFileType(
            fileTypeDict['name'],
            fileTypeDict['shortName'],
            fileTypeDict['extensions']
        )

    def __init__(self, name, shortname, extensions = () ):
        """
        Args:
            name (str)
            shortName (str)
            extensions (list of str)
        """
        super(RamFileType, self).__init__( name, shortname )

        self._extensions = []
        for extension in extensions:
            if not extension.startswith('.'):
                extension = '.' + extension
            self._extensions.append(extension)

    def extensions( self ):
        """The extensions which can be used for this file type, including the “.”

        Returns:
            list of string
        """
        return self._extensions

    def check(self, filePath):
        """Checks if the given file is of this type"""

        fileBlocks = filePath.split('.')

        if len(fileBlocks) < 2:
            return False

        fileExt = '.' + fileBlocks[-1]

        if fileExt in self._extensions:
            return True
        return False