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

    def absolutePath( self, relativePath="" ):
        """Builds an absolute path from a path relative to the project path

        Args:
            relativePath (str)

        Returns:
            str
        """
        return self._folderPath + '/' + relativePath

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

        groupsToCheck = []
        assetsList = []
        newAssetsList = []

        # If we're online, ask the client (return a dict)
        if Ramses.instance.online:
            assetsDict = self._daemon.getAssets()
            # check if successful
            if RamDaemonInterface.checkReply( assetsDict ):
                content = assetsDict['content']
                foundAssets = content['assets']
                if groupName == "":
                    for assetDict in foundAssets:
                        assetsList.append( RamAsset( assetDict['name'], assetDict['shortName'], assetDict['folder'], assetDict['group'], assetDict['tags'] ) )
                    return assetsList
                else:
                    for assetDict in foundAssets:
                        log( "Checking this group: " + str( assetDict ) )
                        if assetDict.get( 'group' ) == groupName:
                             assetsList.append( RamAsset( assetDict['name'], assetDict['shortName'], assetDict['folder'], assetDict['group'], assetDict['tags'] ) )
                    return assetsList

        # Else, check in the folders
        assetsFolderPath = self._folderPath + '/04-ASSETS'

        if groupName == "": #List all assets and groups found at the root
            foundFiles = os.listdir( assetsFolderPath )
            for foundFile in foundFiles:
                if not os.path.isdir( assetsFolderPath + '/' + foundFile ): continue
                if Ramses.instance._isRamsesItemFoldername( n = foundFile ):
                    if not foundFile.split( '_' )[1] == 'A': continue
                    foundAssetName = foundFile.split( '_' )[2]
                    foundAssetPath = "04-ASSETS/" + foundFile
                    foundAsset = RamAsset(assetName = "", assetShortName = foundAssetName, assetFolder = foundAssetPath, assetGroup = "", assetTags = "" )
                    newAssetsList.append( foundAsset )
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
                foundAsset = RamAsset( assetName = "", assetShortName = foundAssetName, assetFolder = foundAssetPath, assetGroup = "", assetTags = "" )
                newAssetsList.append( foundAsset )
        
        return newAssetsList

    def assetGroups( self ): 
        """Available asset groups in this project

        Returns:
            list of str
        """
        assetGroups = []

        if not Ramses.instance:
            raise Exception( "Ramses has to be instantiated first." )

        # If we're online, ask the client
        if Ramses.instance.online:
            assetsDict = self._daemon.getAssetGroups()
            # check if successful
            # if RamDaemonInterface.checkReply( assetsDict ):  ATTENTION : à décommenter quand daemon OK

            for foundFile in assetsDict:
                groupName = foundFile['name']
                assetGroups.append(groupName)
            return assetGroups

        # Else check in the folders
        assetsFolderPath = self._folderPath + '/04-ASSETS'
        if not os.path.isdir( assetsFolderPath ):
            raise Exception( "The asset folder for " + self._name + " (" + self._shortName + ") " + "could not be found." )

        foundFiles = os.listdir( assetsFolderPath )

        for foundFile in foundFiles:
            if not os.path.isdir( assetsFolderPath + '/' + foundFile ): continue
            if Ramses.instance._isRamsesItemFoldername( foundFile ): continue
            assetGroups.append( foundFile )

        return assetGroups

    def shots( self, filter = "*" ):  
        """Available shots in this project

        Args:
            filter

        Returns:
            list of RamShot
        """
        if not Ramses.instance:
            raise Exception( "Ramses has to be instantiated first." )

        # If we're online, ask the client (return a dict)
        shotsList = []
        if Ramses.instance.online:
            shotsDict = self._daemon.getShots()
            # check if successful
            if RamDaemonInterface.checkReply( shotsDict ):
                content = shotsDict['content']
                foundShots = content['shots']
                for shotDict in foundShots:
                    shotsList.append( RamShot( shotDict['name'], shotDict['shortName'], shotDict['folder'], shotDict['duration'] ))

                return shotsList

        # Else check in the folders
        shotsFolderPath = self._folderPath + '/05-SHOTS'

        if not os.path.isdir( shotsFolderPath ):
            return []

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
            foundShot = RamShot( shotName = "", shotShortName = foundShotName , shotFolderPath = foundShotPath )
            foundShots.append( foundShot )

        return foundShots

    def steps( self, stepType=StepType.ALL ): #TODO finir le offline
        """Available steps in this project. Use type to filter the results.
            One of: RamStep.ALL, RamStep.ASSET_PODUCTION, RamStep.SHOT_PRODUCTION, RamStep.PRE_PRODUCTION, RamStep.PRODUCTION, RamStep.POST_PRODUCTION.
            RamStep.PRODUCTION represents a combination of SHOT and ASSET

        Args:
            typeStep (enumerated value, optional): Defaults to RamStep.ALL.

        Returns:
            list of RamStep
        """
        if not Ramses.instance:
            raise Exception( "Ramses has to be instantiated first." )

        stepsList = []

        # If we're online, ask the client (return a dict)
        if Ramses.instance.online:
            stepsDict = self._daemon.getSteps()
            # check if successful
            if RamDaemonInterface.checkReply( stepsDict ):
                content = stepsDict['content']
                foundSteps = content['steps']
                if stepType == StepType.ALL:
                    for stepDict in foundSteps :
                        stepsList.append( RamStep( stepDict['name'], stepDict['shortName'], stepDict['folder'], stepDict['type'] ) )
                    return stepsList
                else:
                    for stepDict in foundSteps:
                        log( "Checking this type : " + str( stepDict ) )
                        if stepDict.get( 'type' ) == stepType:
                            stepsList.append( RamStep( stepDict['name'], stepDict['shortName'], stepDict['folder'], stepDict['type'] ) )
                    return stepsList

        # Else, check in the folders
        stepsFolderPath = self._folderPath 
        # faire avec 01-PRE-PROD, 02-PROD, 03-POST-PROD
        # dans PROJECTID_MOD "mod" c'est le shortname
        # check https://ramses-docs.rainboxlab.org/files/tree/



            


    def folderPath( self ):
        return self.absolutePath( )