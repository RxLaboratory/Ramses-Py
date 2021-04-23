import os

from .logger import log
from .ramses import Ramses
from .ramItem import RamItem


class RamShot( RamItem ):
    """A shot"""

    def __init__( self, shotName, shotShortName ):
        """
        Args:
            shotName (str)
            shotShortName (str)
        """
        super().__init__( shotName, shotShortName )

    def duration( self ):
        """The shot duration, in seconds

        Returns:
            float
        """
        return self._duration

    @staticmethod
    def getFromPath( folderPath ):
        """Returns a RamShot instance built using the given folder path.
            The path can be any file or folder path from the asset
            (a version file, a preview file, etc)

        Args:
            folderPath (str)

        Returns:
            RamShot
        """
        if not Ramses.instance:
            raise Exception( "Ramses has to be instantiated first." )
        if not os.path.isdir( folderPath ):
            folderPath = Ramses.instance.currentProject().getAbsolutePath( folderPath )  # A vérifier... currentProject()
            if not os.path.isdir( folderPath ):
                log( "The given folder could not be found" )
                return None
        
        folderName = os.path.basename( folderPath )

        if not Ramses.instance._isRamsesItemFoldername( folderName ):
            log( "The given folder does not respect Ramses' naming convention" )
            return None

        folderBlocks = folderName.split( '_' )

        if not folderBlocks[ 1 ] == 'S':
            log( "The given folder does not belong to a shot" )
            return None

        shortName = folderBlocks[ 2 ]
        shotFolderPath = os.path.relpath( folderPath, Ramses.instance.currentProject.folderPath )

        shot = RamShot( shotName = shortName, folderPath = shotFolderPath )
        return shot
