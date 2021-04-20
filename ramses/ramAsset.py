import os

from . import log
from .ramItem import RamItem
from .ramses import Ramses


class RamAsset( RamItem ):
    """A class representing an asset."""

    def __init__(self, assetName, assetShortName):
        """[summary]

        Args:
            assetName ([type]): [description]
            assetShortName ([type]): [description]
        """
        self._assetName = assetName
        self._assetShortName = assetShortName

    def tags( self ):
        """Some tags describing the asset.
        return list of string
        """
        return self.tags

    def group( self ):
        """The group containing this asset.
        return string
        """
        return self.group

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
            folderPath = Ramses.instance.currentProject.getAbsolutePath( folderPath )
            if not os.path.isdir( folderPath ):
                log("The given folder could not be found")
                return None

        folderName = os.path.baseName( folderPath )

        if not Ramses.instance._isRamsesItemFoldername( folderName ):
            log( "The given folder does not respect Ramses' naming convention" )
            return None
        
        folderBlocks = folderName.split( '_' )

        if not folderBlocks[ 1 ] == 'A':
            log( "The given folder does not belong to an asset" )
            return None

        shortName = folderBlocks[ 2 ]
        assetFolderPath = os.path.relpath(folderPath, Ramses.instance.currentProject.folderPath )

        asset = RamAsset(assetName = shortName, assetShortName = shortName, folderPath = assetFolderPath)
        return asset

