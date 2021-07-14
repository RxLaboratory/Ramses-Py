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