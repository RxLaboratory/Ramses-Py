from .ramItem import RamItem
from .ramSettings import ItemType
from .daemon_interface import RamDaemonInterface
from . import Ramses

# Keep the daemon at hand
daemon = RamDaemonInterface.instance()

class RamShot( RamItem ):
    """A shot"""

    @staticmethod
    def fromDict( shotDict ):
        """Builds a RamShot from dict like the ones returned by the RamDaemonInterface"""

        s = RamShot(
            shotDict['name'],
            shotDict['shortName'],
            shotDict['folder'],
            shotDict['duration']
        )
        return s

    @staticmethod
    def fromPath( path ):
        """Returns a RamShot instance built using the given path.
            The path can be any file or folder path from the asset
            (a version file, a preview file, etc)

        Args:
            path (str)

        Returns:
            RamShot
        """
        shot = RamItem.fromPath( path )

        if not shot:
            return None

        if not shot.itemType() == ItemType.SHOT:
            return None

        return shot

    def __init__( self, shotName, shotShortName, shotFolder="", duration=0.0 ):
        """
        Args:
            shotName (str)
            shotShortName (str)
        """
        super().__init__( shotName, shotShortName, shotFolder, ItemType.SHOT )
        self._duration = duration

    def duration( self ): # Mutable
        """The shot duration, in seconds

        Returns:
            float
        """

        if Ramses.instance().online():
            shotDict = daemon.getShot( self._shortName )
            # check if successful
            if RamDaemonInterface.checkReply( shotDict ):
                content = shotDict['content']
                self._duration = content['duration']
                
        return self._duration

    # Hidden and not documented: documented in RamItem.folderPath()
    def folderPath( self, step="" ): # Immutable 
        """Re-implemented from RamItem to pass it the type"""
        return super().folderPath( step )
