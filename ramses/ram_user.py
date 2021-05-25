# -*- coding: utf-8 -*-

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
            role
        )

    def __init__( self, userName, userShortName, userFolderPath="", role=UserRole.STANDARD ):
        """
        Args:
            userName (str)
            userShortName (str)
            userFolderPath (str, optional): Defaults to "".
            role (str, optional): (Read-only) enumerated value. Defaults to 'STANDARD'.
                'ADMIN', 'PROJECT_ADMIN', 'LEAD', or 'STANDARD'
        """
        super().__init__( userName, userShortName )
        self._folderPath = userFolderPath
        self._role = role

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

        path = FolderNames.userConfig
        return self.folderPath() + "/" + path

    def folderPath( self ):
        """The absolute path to the user folder

        Returns:
            str
        """
        return self._folderPath

