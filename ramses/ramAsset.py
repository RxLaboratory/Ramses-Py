import os

from . import Ramses
from .logger import log, Log, LogLevel
from .ramItem import RamItem
from .ramSettings import ItemType
from .daemon_interface import RamDaemonInterface

# Keep the daemon at hand
daemon = RamDaemonInterface.instance()

class RamAsset( RamItem ):
    """A class representing an asset."""

    @staticmethod
    def fromDict( assetDict ):
        """Builds a RamAsset from dict like the ones returned by the RamDaemonInterface"""

        a = RamAsset( assetDict['name'],
                      assetDict['shortName'],
                      assetDict['folder'],
                      assetDict['group'],
                      assetDict['tags'] )
        return a

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

    def __init__(self, assetName, assetShortName, assetFolder="", assetGroupName="", tags=()):
        """
        Args:
            assetName (str)
            assetShortName (str)
            assetFolder (str)
            assetGroupName (str)
            tags (list of str)
        """
        super().__init__( assetName, assetShortName, assetFolder, ItemType.ASSET )
        if tags is None:
            tags = []
        self._group = assetGroupName
        self._tags = tags

    def tags( self ): # Mutable
        """Some tags describing the asset. An empty list if the Daemon is not available.

        Returns:
            list of str
        """

        if Ramses.instance().online():
            assetDict = daemon.getAsset( self._shortName )
            # check if successful
            if RamDaemonInterface.checkReply( assetDict ):
                content = assetDict['content']
                self._tags = content['tags']

        return self._tags

    def group( self ): # Immutable
        """The name of group containing this asset. (e.g. Props)

        Returns:
            str
        """

        if self._group != "":
            return self._group

        # If we're online, ask the client (return a dict)
        if Ramses.instance().online():
            assetDict = daemon.getAsset( self._shortName )
            # check if successful
            if RamDaemonInterface.checkReply( assetDict ):
                content = assetDict['content']
                self._group = content['group']

        # Else, check in the folders
        folderPath = self.folderPath()

        if not os.path.isdir( folderPath ):
            log( Log.PathNotFound + " " + folderPath, LogLevel.Critical )
            return self._group

        parentFolder = os.path.dirname( folderPath )
        parentFolderName = os.path.basename( parentFolder )

        if parentFolderName != '04-ASSETS':
            self._group = parentFolderName
        else:
            self._group = ''
            
        return self._group

    # Hidden and not documented: documented in RamItem.folderPath()
    def folderPath( self, step="" ): # Immutable
        """Re-implemented from RamItem to pass it the type and group name"""
        return super().folderPath( self.group())

    # Hidden and not documented: documented in RamItem.stepPath()
    def stepPath( self, step="" ): # Immutable
        """Re-implemented from RamItem to pass it the type and group name"""
        return super().stepPath( step, self.group())

