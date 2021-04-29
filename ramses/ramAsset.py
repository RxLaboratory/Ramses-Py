import os

from . import Ramses
from .logger import log
from .ramItem import RamItem


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
        super().__init__( assetName, assetShortName, assetFolder )
        if tags is None:
            tags = []
        self._group = assetGroupName
        self._tags = tags

    def tags( self ):
        """Some tags describing the asset.

        Returns:
            list of str
        """
        return self._tags

    def group( self ):
        """The group containing this asset.

        Returns:
            str
        """
        if not Ramses.instance:
            raise Exception( "Ramses has to be instantiated first." )

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
    def getFromPath( folderPath ):
        """Returns a RamAsset instance built using the given path.
        The path can be any file or folder path from the asset 
        (a version file, a preview file, etc)

        Args:
            folderPath (str)

        Returns:
            RamAsset
        """
        if not Ramses.instance:
            raise Exception( "Ramses has to be instantiated first." )
        if not os.path.isdir( folderPath ):
            folderPath = Ramses.instance.currentProject().absolutePath( folderPath )
            if not os.path.isdir( folderPath ):
                log( "The given folder could not be found" )
                return None

        folderName = os.path.basename( folderPath )

        if not Ramses.instance._isRamsesItemFoldername( folderName ):
            log( "The given folder does not respect Ramses' naming convention" )
            return None
        
        folderBlocks = folderName.split( '_' )

        if not folderBlocks[ 1 ] == 'A':
            log( "The given folder does not belong to an asset" )
            return None

        shortName = folderBlocks[ 2 ]
        assetFolderPath = os.path.relpath( folderPath, Ramses.instance.currentProject().folderPath )

        asset = RamAsset( assetName = "", assetShortName = shortName, assetFolder = assetFolderPath )
        return asset

    # Hidden and not documented: documented in RamItem.folderPath()
    def folderPath( self, step="" ):    # def folderPath( self, itemType='ASSET', step="", assetGroup=None  ):
        """Re-implemented from RamItem to pass it the type and group name"""
        return super().folderPath('ASSET', step, self.group())
