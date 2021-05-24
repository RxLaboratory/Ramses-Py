from .ram_item import RamItem
from .daemon_interface import RamDaemonInterface
from .constants import ItemType
from .ramses import Ramses

# Keep the daemon at hand
daemon = RamDaemonInterface.instance()

class RamShot( RamItem ):
    """A shot"""

    @staticmethod
    def fromDict( shotDict ):
        """Builds a RamShot from dict like the ones returned by the RamDaemonInterface"""

        return RamShot(
            shotDict['name'],
            shotDict['shortName'],
            shotDict['folder'],
            shotDict['duration']
        )

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
        super(RamShot, self).__init__( shotName, shotShortName, shotFolder, ItemType.SHOT )
        self._duration = duration

    def duration( self ): # Mutable
        """The shot duration, in seconds

        Returns:
            float
        """

        if Ramses.instance().online():
            reply = daemon.getShot( self._shortName )
            # check if successful
            if RamDaemonInterface.checkReply( reply ):
                self._duration = reply['content']['duration']
                
        return self._duration
