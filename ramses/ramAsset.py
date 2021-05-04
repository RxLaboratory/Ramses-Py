import os

from . import Ramses
from .logger import log, Log, LogLevel
from .ramItem import RamItem
from .file_manager import RamFileManager
from .ramSettings import ItemType


class RamAsset( RamItem ):
    """A class representing an asset."""

    @staticmethod
    # documented in RamItem.getFromPath()
    def getFromPath( fileOrFolderPath ):
        """Returns a RamAsset instance built using the given path.
            The path can be any file or folder path from the asset
            (a version file, a preview file, etc)

        Args:
            path (str)

        Returns:
            RamAsset
        """
        asset = RamItem.getFromPath( fileOrFolderPath )

        if not asset:
            return None

        if not asset.itemType() == ItemType.ASSET:
            return None

        return asset

    def __init__(self, assetName, assetShortName, assetFolder="", assetGroupName="", tags=[]):
        """
        Args:
            assetName (str)
            assetShortName (str)
            assetFolder (str)
            assetGroupName (str)
            tags (list of str)
        """
        super().__init__( assetName, assetShortName, assetFolder, ItemType.ASSET )
        self._group = assetGroupName
        self._tags = tags

    def tags( self ): # Mutable #TODO online
        """Some tags describing the asset. An empty list if the Daemon is not available.

        Returns:
            list of str
        """

        if Ramses.instance().online():
            #TODO demander au démon
            pass

        return self._tags

    def group( self ): # Immutable #TODO online
        """The name of group containing this asset. (e.g. Props)

        Returns:
            str
        """

        if self._group != "":
            return self._group

        if Ramses.instance().online():
            #TODO demander au démon
            pass

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
        return super().folderPath( ItemType.ASSET, step, self.group())

