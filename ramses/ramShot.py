import os

from .logger import log
from .ramItem import RamItem, ItemType
from .file_manager import RamFileManager
from . import Ramses


class RamShot( RamItem ):
    """A shot"""

    def __init__( self, shotName, shotShortName, shotFolder, duration=0.0 ):
        """
        Args:
            shotName (str)
            shotShortName (str)
        """
        super().__init__( shotName, shotShortName, shotFolder, ItemType.SHOT )
        self._duration = duration

    def duration( self ):
        """The shot duration, in seconds

        Returns:
            float
        """
        return self._duration

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

    # Hidden and not documented: documented in RamItem.folderPath()
    def folderPath( self, step="" ):   # def folderPath( self, itemType='SHOT', step="", assetGroup=None ):
        """Re-implemented from RamItem to pass it the type"""
        return super().folderPath( ItemType.SHOT, step)
