import os
import re

from .logger import log
from .ramObject import RamObject
from .ramses import Ramses
from .ramStep import RamStep, StepType
from .ramAsset import RamAsset
from .ramShot import RamShot
from .utils import escapeRegEx
from .daemon_interface import RamDaemonInterface


class RamProject( RamObject ):
    """A project handled by Ramses. Projects contains general items, assets and shots."""

    def __init__( self, projectName, projectShortName, projectPath, width, height, framerate ):
        """
        Args:
            projectName (str)
            projectShortName (str)
            projectPath (str)
            width (int)
            height (int)
            framerate (float)
        """
        super().__init__( projectName, projectShortName )
        self._folderPath = projectPath
        self._daemon = RamDaemonInterface()
        self._width = width
        self._height = height
        self._framerate = framerate

    def width( self ): #TODO
        """
        Returns:
            int
        """
        # if not Ramses.instance:
        #     raise Exception( "Ramses has to be instantiated first." )
        # # If we're online, ask the client
        # if Ramses.instance.online:
        #     # TODO ask the client
        #     return None

        return self._width

    def height( self ): #TODO
        """
        Returns:
            int
        """
        return self._height

    def framerate( self ): #TODO
        """
        Returns:
            float
        """
        return self._framerate


    def absolutePath( self, relativePath ):
        """Builds an absolute path from a path relative to the project path

        Args:
            relativePath (str)

        Returns:
            str
        """
        return self._folderPath + '/' + relativePath

    def assets( self, groupName="" ):  #TODO if online à vérifier
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

        groupsToCheck = []
        foundAssets = []

        # If we're online, ask the client (return a dict)
        if Ramses.instance.online:
            assetsDict = self._daemon.getAssets()
            # check if successful
            if RamDaemonInterface.checkReply( assetsDict ):
                content = assetsDict['content']
                foundFiles = content['assets']
                if groupName == "":
                    return foundFiles
                else:
                    for files in foundFiles:
                        log( "Checking this group: " + str(files) )
                        if files.get("group") == groupName:
                            foundAssets.append(files)
                    return foundAssets

        # Else check in the folders
        assetsFolderPath = self._folderPath + '/04-ASSETS'


        if groupName == "": #List all assets and groups found at the root
            foundFiles = os.listdir( assetsFolderPath )
            for foundFile in foundFiles:
                if not os.path.isdir( assetsFolderPath + '/' + foundFile ): continue
                if Ramses.instance._isRamsesItemFoldername( n = foundFile ):
                    if not foundFile.split( '_' )[1] == 'A': continue
                    foundAssetName = foundFile.split( '_' )[2]
                    foundAssetPath = "04-ASSETS/" + foundFile
                    foundAsset = RamAsset(assetName = foundAssetName, assetShortName = foundAssetName, assetFolder = foundAssetPath )
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
                foundAsset = RamAsset( assetName = foundAssetName, assetShortName = foundAssetName, assetFolder = foundAssetPath )
                foundAssets.append( foundAsset )
        
        return foundAssets

    def assetGroups( self ): #TODO if online
        """Available asset groups in this project

        Returns:
            list of str
        """
        if not Ramses.instance:
            raise Exception( "Ramses has to be instantiated first." )

        # If we're online, ask the client
        if Ramses.instance.online:
            # TODO
            return None

        # Else check in the folders
        assetsFolderPath = self._folderPath + '/04-ASSETS'
        if not os.path.isdir( assetsFolderPath ):
            raise Exception( "The asset folder for " + self._name + " (" + self._shortName + ") " + "could not be found." )

        foundFiles = os.listdir( assetsFolderPath )
        assetGroups = []

        for foundFile in foundFiles:
            if not os.path.isdir( assetsFolderPath + '/' + foundFile ): continue
            if Ramses.instance._isRamsesItemFoldername( foundFile ): continue
            assetGroups.append( foundFile )

        return assetGroups

    def shots( self ):  #TODO if online
        """Available shots in this project

        Returns:
            list of RamShot
        """
        if not Ramses.instance:
            raise Exception( "Ramses has to be instantiated first." )

        # If we're online, ask the client
        if Ramses.instance.online:
            # TODO
            return None

        # Else check in the folders
        shotsFolderPath = self._folderPath + '/05-SHOTS'
        if not os.path.isdir( shotsFolderPath ):
            raise Exception( "The asset folder for " + self._name + " (" + self._shortName + ") " + "could not be found." )

        if filter != "" and not "*" in filter: #User is looking for a specific shot: no need to parse through everything
            foundShotPath = shotsFolderPath + '/' + self._shortName + '_S_' + filter
            if not os.path.isdir( foundShotPath ):
                print( "Shot " + filter + " was not found." )
                return []
            return [RamShot( shotName = filter, folderPath = foundShotPath )]

        if "*" in filter and filter != "*": #Preparing regex for wildcards
            filter = escapeRegEx( filter )
            filter = filter.replace( '\\*' , '([a-z0-9+-]{1,10})?' )
            regex = re.compile( filter, re.IGNORECASE )
        
        foundFiles = os.listdir( shotsFolderPath )
        foundShots = []

        for foundFile in foundFiles:
            if not os.path.isdir( shotsFolderPath + '/' + foundFile ): continue
            if not Ramses.instance._isRamsesItemFoldername( foundFile ): continue
            if not foundFile.split('_')[1] == 'S': continue

            foundShotName = foundFile.split('_')[2]
            
            if not filter in ( "" , "*" ):
                if not re.match( regex, foundShotName ):
                    continue

            foundShotPath = shotsFolderPath + '/' + foundFile
            foundShot = RamShot( shotName = foundShotName , folderPath = foundShotPath )
            foundShots.append( foundShot )

        return foundShots

    def steps( self, stepType=StepType.ALL ): #TODO
        """Available steps in this project. Use type to filter the results.
            One of: RamStep.ALL, RamStep.ASSET_PODUCTION, RamStep.SHOT_PRODUCTION, RamStep.PRE_PRODUCTION, RamStep.PRODUCTION, RamStep.POST_PRODUCTION.
            RamStep.PRODUCTION represents a combination of SHOT and ASSET

        Args:
            typeStep (enumerated value, optional): Defaults to RamStep.ALL.

        Returns:
            list of RamStep
        """
        pass
