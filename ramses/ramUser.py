from .ramObject import RamObject


class RamUser( RamObject ):
    """The class representing users."""

    def __init__( self, userName, userShortName, userFolderPath="", role='STANDARD' ):
        """
        Args:
            userName (str): [description]
            userShortName (str): [description]
            userFolderPath (str, optional): [description]. Defaults to "".
            role (str, optional): (Read-only) enumerated value. Defaults to 'STANDARD'.
                'ADMIN', 'PROJECT_ADMIN', 'LEAD', or 'STANDARD'
        """
        self.name = userName
        self.shortName = userShortName
        self.folderPath = userFolderPath
        self._role = 'STANDARD'

    @property
    def role( self ):
        """
        Returns:
            (Read-only) enumerated value: 'ADMIN', 'PROJECT_ADMIN', 'LEAD', or 'STANDARD'
        """
        return self._role

    def configPath( self ): #TODO
        """The path to the Config folder relative to the user folder

        Returns:
            str
        """
        pass

    def folderPath( self ): #TODO
        """The absolute path to the user folder

        Returns:
            str
        """
        pass
