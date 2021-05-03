import os

from . import Ramses
from .logger import log
from .ramItem import RamItem, ItemType
from .file_manager import RamFileManager


class RamAsset( RamItem ):
    """A class representing an asset."""

    def __init__(self, assetName, assetShortName, assetFolder, assetGroupName="", tags=None):
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

    def tags( self ):
        """Some tags describing the asset. An empty list if the Daemon is not available.

        Returns:
            list of str
        """
        return self._tags

    def group( self ):
        """The name of group containing this asset. (e.g. Props)

        Returns:
            str
        """

        if self._group != "":
            return self._group

        if self._folderPath == '':
            log( "The given item has no folderPath." )
            return self._group
        if not os.path.isdir( self._folderPath ):
            log( "The given item's folder was not found.\nThis is the path that was checked:\n" + self._folderPath )
            return self._group

        parentFolder = os.path.dirname( self._folderPath )
        parentFolderName = os.path.basename( parentFolder )

        if parentFolderName != '04-ASSETS':
            return parentFolderName
            
        return self._group

    @staticmethod
    def getFromPath( path ):
        """Returns a RamAsset instance built using the given path.
            The path can be any file or folder path from the asset
            (a version file, a preview file, etc)

        Args:
            path (str)

        Returns:
            RamAsset
        """
        asset = RamItem.getFromPath( path )

        if not asset:
            return None

        if not asset.itemType() == ItemType.ASSET:
            return None

        return asset

    # Hidden and not documented: documented in RamItem.folderPath()
    def folderPath( self, step="" ):    # def folderPath( self, itemType='ASSET', step="", assetGroup=None  ):
        """Re-implemented from RamItem to pass it the type and group name"""
        return super().folderPath( ItemType.ASSET, step, self.group())
