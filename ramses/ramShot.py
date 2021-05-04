import os

from .logger import log
from .ramItem import RamItem
from .file_manager import RamFileManager
from .ramSettings import ItemType
from . import Ramses

class RamShot( RamItem ):
    """A shot"""

    @staticmethod
    def getFromPath( path ):
        """Returns a RamShot instance built using the given path.
            The path can be any file or folder path from the asset
            (a version file, a preview file, etc)

        Args:
            path (str)

        Returns:
            RamShot
        """
        shot = RamItem.getFromPath( path )

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

    def duration( self ): # Mutable #TODO ask daemon
        """The shot duration, in seconds

        Returns:
            float
        """

        if Ramses.instance().online():
            #TODO demander au démon
            pass

        return self._duration

    # Hidden and not documented: documented in RamItem.folderPath()
    def folderPath( self, step="" ): # Immutable 
        """Re-implemented from RamItem to pass it the type"""
        return super().folderPath( step )
