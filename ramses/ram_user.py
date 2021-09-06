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

from .ram_object import RamObject
from .constants import UserRole, FolderNames

class RamUser( RamObject ):
    """The class representing users."""

    @staticmethod
    def fromDict( userDict ):
        """Builds a RamUser from dict like the ones returned by the RamDaemonInterface"""

        role = UserRole.STANDARD
        if userDict['role'] == 'LEAD':
            role = UserRole.LEAD
        elif userDict['role'] == 'PROJECT_AMIN':
            role = UserRole.PROJECT_ADMIN
        elif userDict['role'] == 'ADMIN':
            role = UserRole.ADMIN

        return RamUser(
            userDict['name'],
            userDict['shortName'],
            userDict['folderPath'],
            role,
            userDict['comment']
        )

    def __init__( self, userName, userShortName, userFolderPath="", role=UserRole.STANDARD, comment=""):
        """
        Args:
            userName (str)
            userShortName (str)
            userFolderPath (str, optional): Defaults to "".
            role (str, optional): (Read-only) enumerated value. Defaults to 'STANDARD'.
                'ADMIN', 'PROJECT_ADMIN', 'LEAD', or 'STANDARD'
        """
        super(RamUser,self).__init__( userName, userShortName )
        self._folderPath = userFolderPath
        self._role = role
        self._comment = comment

    def comment( self ):
        return self._comment

    def role( self ):
        """
        Returns:
            (Read-only) enumerated value: 'ADMIN', 'PROJECT_ADMIN', 'LEAD', or 'STANDARD'
        """
        return self._role

    def configPath( self ): 
        """The path to the Config folder

        Arguments:
            absolute: bool

        Returns:
            str
        """

        path = FolderNames.config
        return self.folderPath() + "/" + path

    def folderPath( self ):
        """The absolute path to the user folder

        Returns:
            str
        """
        return self._folderPath

