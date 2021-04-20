import os

from . import RamAsset, log
from .ramObject import RamObject
from .ramses import Ramses


class RamProject( RamObject ):
    """A project handled by Ramses. Projects contains general items, assets and shots."""

    def __init__( self, projectName, projectShortName, projectPath ):
        """
        Args:
            projectName (str)
            projectShortName (str)
            projectPath (str)
        """
        self.name = projectName
        self.shortName = projectShortName
        self.folderPath = projectPath

    def absolutePath( self, relativePath ):
        """Builds an absolute path from a path relative to the project path

        Args:
            relativePath (str)

        Returns:
            str
        """
        return self.folderPath + '/' + relativePath

    def assets( self, groupName="" ):
        """Available assets in this project and group.
        If groupName is an empty string, returns all assets.

        Args:
            groupName (str, optional): Defaults to "".

        Returns:
            list of RamAsset
        """
        if not Ramses.instance:
            raise Exception( "Ramses has to be instantiated first." )
        if not isinstance( groupName, str ):
            raise TypeError( "Group name must be a str" )

        # If we're online, ask the client
        if Ramses.instance.online:
            #TODO
            return None
        
        # Else check in the folders
        assetsFolderPath = self.folderPath + '/04-ASSETS'
        groupsToCheck = []
        foundAssets = []
        foundFiles = []

        if groupName == "": #List all assets and groups found at the root
            foundFiles = os.listdir( assetsFolderPath )
            for foundFile in foundFiles:
                if not os.path.isdir( assetsFolderPath + '/' + foundFile ): continue
                if Ramses.instance._isRamsesItemFoldername( n = foundFile ):
                    if not foundFile.split( '_' )[1] == 'A': continue
                    foundAssetName = foundFile.split( '_' )[2]
                    foundAssetPath = "04-ASSETS/" + foundFile
                    foundAsset = RamAsset(assetName = foundAssetName, assetShortName = foundAssetName, folderPath = foundAssetPath )
                    foundAssets.append( foundAsset )
                else:
                    groupsToCheck.append( foundFile )
        else:
            if not os.path.isdir( assetsFolderPath + '/' + groupName ):
                log( "The following group of assets: " + groupName + " could not be found" )
                return None
            groupsToCheck.append( groupName )
        
        for group in groupsToCheck:
            log( "Checking this group: " + group )
            foundFiles = os.listdir( assetsFolderPath + '/' + group )
            for foundFile in foundFiles:
                if not os.path.isdir( assetsFolderPath + '/' + group + '/' + foundFile ): continue
                if not Ramses.instance._isRamsesItemFoldername( foundFile ): continue
                if not foundFile.split( '_' )[1] == 'A': continue
                foundAssetName = foundFile.split( '_' )[2]
                foundAssetPath = "04-ASSETS/" + group + "/" + foundFile
                foundAsset = RamAsset( assetName = foundAssetName, assetShortName = foundAssetName, folderPath = foundAssetPath )
                foundAssets.append( foundAsset )
        
        return foundAssets
