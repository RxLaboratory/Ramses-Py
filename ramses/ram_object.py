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

class RamObject(object):
    """The base class for most of Ramses objects."""

    @staticmethod
    def fromDict( objectDict ):
        """Builds a RamObject from dict like the ones returned by the RamDaemonInterface"""

        return RamObject(
            objectDict['name'],
            objectDict['shortName']
        )

    @staticmethod
    def getObjectShortName( obj ):
        from .file_manager import RamFileManager

        if isinstance( obj, RamObject ):
            shortName = obj.shortName()
        elif obj is None:
            return ''
        else:
            shortName = obj

        return shortName

    def __init__( self, objectName, objectShortName ):
        """
        Args:
            objectName (str): May contain spaces, [a-z] ,[A-Z], [0-9], [+-], limited to 256 characters
            objectShortName (str):  Used for compact display and folder names, limited to 10 characters,
                must not contain spaces, may contain [a-z] ,[A-Z], [0-9], [+-].
        """

        from .file_manager import RamFileManager

        self._name = objectName
        self._shortName = objectShortName
    
    def name( self ):
        """
        Returns:
            str
        """
        return self._name

    def shortName( self ):
        """
        Returns:
            str
        """
        return self._shortName

    def __str__( self ):
        n = self._shortName
        if self._name != '':
            if n != '': n = n + " | "
            n = n + self._name
        return n

    def __eq__(self, other):
        try:
            return self._shortName == other._shortName
        except:
            return False
