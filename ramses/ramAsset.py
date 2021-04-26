import os

from .logger import log
from .ramses import Ramses
from .ramItem import RamItem

class RamAsset( RamItem ):
    """A class representing an asset."""

    def __init__( self, assetName, assetShortName, assetFolder="" ):
        """
        Args:
            assetName (str)
            assetShortName (str)
            assetFolder (str)
        """
        super().__init__( assetName, assetShortName )
        self._assetFolder = assetFolder


    def tags( self ): #TODO
        """Some tags describing the asset.

        Returns:
            list of str
        """
        pass

    def group( self ): #TODO if online
        """The group containing this asset.

        Returns:
            str
        """
        if not Ramses.instance:
            raise Exception( "Ramses has to be instantiated first." )
        # If we're online, ask the client
        if Ramses.instance.online:
            #TODO
            return None

        if self.folderPath == '':
            print( "The given item has no folderPath." )
            return None
        if not os.path.isdir( self._folderPath ):
            print( "The given item's folder was not found.\nThis is the path that was checked:\n" + self._folderPath )
            return None

        parentFolder = os.path.dirname( self._folderPath )
        parentFolderName = os.path.basename( parentFolder )

        if parentFolderName != '04-ASSETS':
            return parentFolderName
            
        return None

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
        assetFolderPath = os.path.relpath( folderPath, Ramses.instance.currentProject.folderPath )

        asset = RamAsset( assetName = shortName, assetShortName = shortName, folderPath = assetFolderPath )
        return asset

