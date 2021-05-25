import os

from . import Ramses
from .logger import log
from .ram_item import RamItem
from .constants import ItemType, Log, LogLevel
from .daemon_interface import RamDaemonInterface

# Keep the daemon at hand
daemon = RamDaemonInterface.instance()

class RamAsset( RamItem ):
    """A class representing an asset."""

    @staticmethod
    def fromDict( assetDict ):
        """Builds a RamAsset from dict like the ones returned by the RamDaemonInterface"""

        return RamAsset(
            assetDict['name'],
            assetDict['shortName'],
            assetDict['folder'],
            assetDict['group'],
            assetDict['tags']
            )

    @staticmethod
    # documented in RamItem.getFromPath()
    def fromPath( fileOrFolderPath ):
        """Returns a RamAsset instance built using the given path.
            The path can be any file or folder path from the asset
            (a version file, a preview file, etc)

        Args:
            fileOrFolderPath (str)

        Returns:
            RamAsset
        """
        asset = RamItem.getFromPath( fileOrFolderPath )

        if not asset:
            return None

        if not asset.itemType() == ItemType.ASSET:
            return None

        return asset

    def __init__(self, assetName, assetShortName, assetFolder="", assetGroup="", tags=() ):
        """
        Args:
            assetName (str)
            assetShortName (str)
            assetFolder (str)
            assetGroupName (str)
            tags (list of str)
        """
        super().__init__( assetName, assetShortName, assetFolder, ItemType.ASSET, assetGroup )
        self._tags = tags

    def tags( self ): # Mutable
        """Some tags describing the asset. An empty list if the Daemon is not available.

        Returns:
            list of str
        """

        if Ramses.instance().online():
            reply = daemon.getAsset( self._shortName )
            # check if successful
            if RamDaemonInterface.checkReply( reply ):
                self._tags = reply['content']['tags']

        return self._tags



