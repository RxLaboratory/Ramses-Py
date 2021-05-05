import os
import re

from .daemon_interface import RamDaemonInterface
from .file_manager import RamFileManager
from .logger import Log, LogLevel, log
from .ramAsset import RamAsset
from .ramObject import RamObject
from .ramses import Ramses
from .ramShot import RamShot
from .ramState import RamState
from .ramStep import RamStep, StepType
from .utils import escapeRegEx, removeDuplicateObjectsFromList

daemon = RamDaemonInterface.instance()

class RamProject( RamObject ):
    """A project handled by Ramses. Projects contains general items, assets and shots."""

    def __init__( self, projectName, projectShortName, projectPath='', width=1920, height=1080, framerate=24.0 ):
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
        self._width = width
        self._height = height
        self._framerate = framerate

    def width( self ): #Mutable #TODO if online
        """
        Returns:
            int
        """

        return self._width

    def height( self ): #Mutable #TODO if online
        """
        Returns:
            int
        """
        return self._height

    def framerate( self ): #Mutable #TODO if online
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
        return RamFileManager.buildPath((
            self.folderPath(),
            relativePath
        ))

    def adminPath( self ):
        """Returns the path of the Admin folder (creates it if it does not exist yet)"""
        projectFolder = self.folderPath()
        if not os.path.isdir( projectFolder ):
            return ''

        thePath = RamFileManager.buildPath((
            projectFolder,
            '00-ADMIN'
        ))

        if not os.path.isdir( thePath ):
            os.makedirs( thePath )
        
        return thePath

    def preProdPath( self ):
        """Returns the path of the PreProd folder (creates it if it does not exist yet)"""
        projectFolder = self.folderPath()
        if not os.path.isdir( projectFolder ):
            return ''

        thePath = RamFileManager.buildPath((
            projectFolder,
            '01-PRE-PROD'
        ))

        if not os.path.isdir( thePath ):
            os.makedirs( thePath )

        return thePath

    def prodPath( self ):
        """Returns the path of the Prod folder (creates it if it does not exist yet)"""
        projectFolder = self.folderPath()
        if not os.path.isdir( projectFolder ):
            return ''

        thePath = RamFileManager.buildPath((
            projectFolder,
            '02-PROD'
        ))

        if not os.path.isdir( thePath ):
            os.makedirs( thePath )

        return thePath

    def postProdPath( self ):
        """Returns the path of the PostProd folder (creates it if it does not exist yet)"""
        projectFolder = self.folderPath()
        if not os.path.isdir( projectFolder ):
            return ''

        thePath = RamFileManager.buildPath((
            projectFolder,
            '03-POST-PROD'
        ))

        if not os.path.isdir( thePath ):
            os.makedirs( thePath )

        return thePath

    def assetsPath( self ):
        """Returns the path of the Assets folder (creates it if it does not exist yet)"""
        projectFolder = self.folderPath()
        if not os.path.isdir( projectFolder ):
            return ''

        thePath = RamFileManager.buildPath((
            projectFolder,
            '04-ASSETS'
        ))

        if not os.path.isdir( thePath ):
            os.makedirs( thePath )
        
        return thePath

    def shotsPath( self ):
        """Returns the path of the Shots folder (creates it if it does not exist yet)"""
        projectFolder = self.folderPath()
        if not os.path.isdir( projectFolder ):
            return ''

        thePath = RamFileManager.buildPath((
            projectFolder,
            '05-SHOTS'
        ))

        if not os.path.isdir( thePath ):
            os.makedirs( thePath )
        
        return thePath

    def exportPath( self ):
        """Returns the path of the Export folder (creates it if it does not exist yet)"""
        projectFolder = self.folderPath()
        if not os.path.isdir( projectFolder ):
            return ''

        thePath = RamFileManager.buildPath((
            projectFolder,
            '06-EXPORT'
        ))

        if not os.path.isdir( thePath ):
            os.makedirs( thePath )
        
        return thePath

    def asset( self, assetShortName ):
        """Gets an asset with its short name.

        Args:
            assetShortName (str): the shortname

        Returns:
            RamAsset
        """
        if not isinstance( assetShortName, str ):
            raise TypeError( "assetShortName must be a str" )

        # If we're online, ask the client (return a dict)
        if Ramses.instance().online():
            assetDict = daemon.getAsset( assetShortName )
            # check if successful
            if RamDaemonInterface.checkReply( assetDict ):
                content = assetDict['content']
                asset = RamAsset( assetName=content['name'], assetShortName=content['shortName'],
                                  assetFolder=content['folder'], assetGroupName=content['group'],
                                  tags=content['tags'])
                return asset

        # Else, check in the folders


    def assets( self, groupName="" ): # Mutable
        """Available assets in this project and group.
        If groupName is an empty string, returns all assets.

        Args:
            groupName (str, optional): Defaults to "".

        Returns:
            list of RamAsset
        """

        if not isinstance( groupName, str ):
            raise TypeError( "Group name must be a str" )

        assetsList = []

        # If we're online, ask the client (return a dict)
        if Ramses.instance().online():
            assetsDict = daemon.getAssets()
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
                        log( "Checking this group: " + str( assetDict ), LogLevel.Debug )
                        if assetDict['group'] == groupName:
                             assetsList.append( RamAsset( assetDict['name'], assetDict['shortName'], assetDict['folder'], assetDict['group'], assetDict['tags'] ) )
                    return assetsList

        # Else, check in the folders
        assetsFolderPath = self.assetsPath()
        if assetsFolderPath == '':
            return assetsList

        return self._getAssetsInFolder( assetsFolderPath, groupName )

    def assetGroups( self ): # Mutable
        """Available asset groups in this project

        Returns:
            list of str
        """
        assetGroups = []

        # If we're online, ask the client
        if Ramses.instance().online():
            assetsDict = daemon.getAssetGroups()
            # check if successful
            if RamDaemonInterface.checkReply( assetsDict ):
                content = assetsDict['content']
                foundAssets = content['assetGroups']

                for foundFile in foundAssets:
                    groupName = foundFile['name']
                    assetGroups.append(groupName)
                return assetGroups

        # Else check in the folders
        assetsFolderPath = self.assetsPath()

        if assetsFolderPath == '':
            return assetGroups

        foundFiles = os.listdir( assetsFolderPath )

        for foundFile in foundFiles:
            if not os.path.isdir( assetsFolderPath + '/' + foundFile ): continue
            if RamFileManager._isRamsesItemFoldername( foundFile ): continue
            assetGroups.append( foundFile )

        return assetGroups

    def shot( self, shotShortName ):
        """Gets a shot with its short name.

        Args:
            shotShortName (str): the shortname

        Returns:
            RamShot
        """

        if not isinstance( shotShortName, str ):
            raise TypeError( "shotShortName must be a str" )

        # If we're online, ask the client (return a dict)
        if Ramses.instance().online():
            shortDict = daemon.getShot( shotShortName )
            # check if successful
            if RamDaemonInterface.checkReply( shortDict ):
                content = shortDict['content']
                shot = RamShot( shotName=content['name'], shotShortName=content['shortName'],
                                shotFolder=content['folder'], duration=content['duration'])

                return shot

        # Else, check in the folders


    def shots( self, nameFilter = "*" ):  #TODO
        """Available shots in this project

        Args:
            nameFilter

        Returns:
            list of RamShot
        """

        shotsList = []

        # If we're online, ask the client (return a dict)
        
        if Ramses.instance().online():
            shotsDict = daemon.getShots()
            # check if successful
            if RamDaemonInterface.checkReply( shotsDict ):
                content = shotsDict['content']
                foundShots = content['shots']
                if nameFilter == "":
                    for shotDict in foundShots:
                        shotsList.append( RamShot( shotDict['name'], shotDict['shortName'], shotDict['folder'], shotDict['duration'] ))
                    return shotsList
                elif "*" in nameFilter and nameFilter != "*": #Preparing regex for wildcards
                    nameFilter = escapeRegEx( nameFilter )
                    nameFilter = nameFilter.replace( '\\*', '([a-z0-9+-]{1,10})?' )
                    regex = re.compile( nameFilter, re.IGNORECASE )
                
                    for shotsDict in foundShots:
                        log( "Checking this filter: " + str( shotsDict ), LogLevel.Debug )


        # Else check in the folders
        shotsFolderPath = self.shotsPath()
        if shotsFolderPath == '':
            return shotsList

        if "*" in nameFilter and nameFilter != "*": #Preparing regex for wildcards
            nameFilter = escapeRegEx( nameFilter )
            nameFilter = nameFilter.replace( '\\*' , '([a-z0-9+-]{1,10})?' )
            regex = re.compile( nameFilter, re.IGNORECASE )
        
        foundFiles = os.listdir( shotsFolderPath )
        foundShots = []

        for foundFile in foundFiles:
            if not os.path.isdir( shotsFolderPath + '/' + foundFile ): continue
            if not RamFileManager._isRamsesItemFoldername( foundFile ): continue
            if not foundFile.split('_')[1] == 'S': continue

            foundShotName = foundFile.split('_')[2]
            
            if not nameFilter in ( "", "*" ):
                if not re.match( regex, foundShotName ):
                    continue

            # foundShotPath = shotsFolderPath + '/' + foundFile
            foundShot = RamShot( shotName = "", shotShortName = foundShotName )
            foundShots.append( foundShot )

        return foundShots

    def state( self, stateShortName ):
        """Gets a state with its short name.

        Args:
            stateShortName ([str])

        Returns:
            [RamState]
        """
        if not isinstance( stateShortName, str ):
            raise TypeError( "stateShortName must be a str" )

        # If we're online, ask the client (return a dict)
        if Ramses.instance().online():
            stateDict = daemon.getState( stateShortName )
            # check if successful
            if RamDaemonInterface.checkReply( stateDict ):
                content = stateDict['content']
                state = RamState( stateName=content['name'], stateShortName=content['shortName'],
                                  completionRatio=content['completionRatio'], color=content['color'])

                return state

    def step( self, stepShortName ):
        """Gets a step with its short name.

        Args:
            stepShortName (str): the shortname

        Returns:
            RamStep
        """
        if not isinstance( stepShortName, str ):
            raise TypeError( "stepShortName must be a str" )

        # If we're online, ask the client (return a dict)
        if Ramses.instance().online():
            stepDict = daemon.getStep( stepShortName )
            # check if successful
            if RamDaemonInterface.checkReply( stepDict ):
                content = stepDict['content']
                step = RamStep( stepName=content['name'], stepShortName=content['shortName'],
                                stepFolder=content['folder'], stepType=content['type'])

                return step

    def steps( self, stepType=StepType.ALL ): # Mutable 
        """Available steps in this project. Use type to filter the results.
            One of: RamStep.ALL, RamStep.ASSET_PODUCTION, RamStep.SHOT_PRODUCTION, RamStep.PRE_PRODUCTION, RamStep.PRODUCTION, RamStep.POST_PRODUCTION.
            RamStep.PRODUCTION represents a combination of SHOT and ASSET

        Args:
            typeStep (enumerated value, optional): Defaults to RamStep.ALL.

        Returns:
            list of RamStep
        """

        stepsList = []

        # If we're online, ask the client (return a dict)
        if Ramses.instance().online():
            stepsDict = daemon.getSteps()
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

        # Check StepType: Pre-Prod
        if stepType == ( StepType.PRE_PRODUCTION or StepType.ALL ):
            stepsFolderPath = self.preProdPath()

            if stepsFolderPath != '':
                preProdFiles = os.listdir( stepsFolderPath )
                for preProdFile in preProdFiles:
                    # we keep only the folders
                    if not os.path.isdir( stepsFolderPath + "/" + preProdFile ):
                        continue

                    preProdFilePath = preProdFile
                    # we split the name of the folders to keep only the step:
                    preProdFileName = preProdFile.split( "_" )[-1]
                    newRamStep = RamStep( stepName="", stepShortName=preProdFileName, stepFolder=preProdFilePath, stepType=StepType.PRE_PRODUCTION )
                    stepsList.append( newRamStep )

        # Check StepType: Prod (assets + shots)
        elif stepType == ( StepType.PRODUCTION or StepType.ALL ):
            stepsFolderPath = self.prodPath()

            if stepsFolderPath != '':
                prodFiles = os.listdir( stepsFolderPath )
                for prodFile in prodFiles:
                    # we keep only the folders
                    if not os.path.isdir( stepsFolderPath + "/" + prodFile ):
                        continue
                    
                    prodFilePath = prodFile
                    # we split the name of the folders to keep only the step:
                    prodFileName = prodFile.split( "_" )[-1]
                    newRamStep = RamStep( stepName="", stepShortName=prodFileName, stepFolder=prodFilePath, stepType=StepType.PRODUCTION )
                    stepsList.append( newRamStep )

        # Check StepType: Post-Prod
        elif stepType == ( StepType.POST_PRODUCTION or StepType.ALL ):
            stepsFolderPath = self.postProdPath()

            if stepsFolderPath != '':
                postProdFiles = os.listdir( stepsFolderPath )
                for postProdFile in postProdFiles:
                    # we keep only the folders
                    if not os.path.isdir( stepsFolderPath + "/" + postProdFile ):
                        continue
                    
                    postProdFilePath = postProdFile
                    # we split the name of the folders to keep only the step:
                    postProdFileName = postProdFile.split( "_" )[-1]
                    newRamStep = RamStep( stepName="", stepShortName=postProdFileName, stepFolder=postProdFilePath, stepType=StepType.POST_PRODUCTION )
                    stepsList.append( newRamStep )

        # Check StepType: Asset
        elif stepType == ( StepType.ALL or StepType.PRODUCTION or StepType.ASSET_PRODUCTION ):
            stepsFolderPath = self.assetsPath()

            if stepsFolderPath !='':
                assetProdFiles = os.listdir( stepsFolderPath )
                for assetProdFile in assetProdFiles:
                    # we keep only the folders
                    # /!\ it's only the groupName folders
                    if not os.path.isdir( stepsFolderPath + "/" + assetProdFile ):
                        continue

                    # search assets with the given groupName:
                    ramAssetList = self.assets( assetProdFile )

                    for ramAssetFile in ramAssetList:
                        if not os.path.isdir( ramAssetFile ):
                            continue

                        assetProdFilePath = ramAssetFile
                        # we split the name of the folders to keep only the step:
                        assetProdFileName = ramAssetFile.split( "_" )[-1]
                        newRamStep = RamStep( stepName="", stepShortName=assetProdFileName, stepFolder=assetProdFilePath, stepType=StepType.ASSET_PRODUCTION )
                        stepsList.append( newRamStep )

        # Check StepType: Shot
        elif stepType == (StepType.ALL or StepType.PRODUCTION or StepType.SHOT_PRODUCTION ):
            stepsFolderPath = self.shotsPath()

            if stepsFolderPath !='':
                shotProdFiles = os.listdir( stepsFolderPath )
                for shotProdFile in shotProdFiles:
                    # we keep only the folders
                    # /!\ it's only the Shots folders
                    if not os.path.isdir( stepsFolderPath + "/" + shotProdFile ):
                        continue

                    # search shots:
                    ramShotList = self.shots( shotProdFile )

                    for ramShotFile in ramShotList:
                        if not os.path.isdir( ramShotFile ):
                            continue

                        shotProdFilePath = ramShotFile
                        # we split the name of the folders to keep only the step:
                        shotProdFileName = shotProdFile.split( "_" )[-1]
                        newRamStep = RamStep( stepName="", stepShortName=shotProdFileName, stepFolder=shotProdFilePath, stepType=StepType.SHOT_PRODUCTION )
                        stepsList.append( newRamStep )    

        return removeDuplicateObjectsFromList( stepsList )

    def project( self, projectShortName ):
        """Gets a project with its short name.

        Args:
            projectShortName (str)

        Returns:
            RamProject
        """
        if not isinstance( projectShortName, str ):
            raise TypeError( "projectShortName must be a str" )

        # If we're online, ask the client (return a dict)
        if Ramses.instance().online():
            projDict = daemon.getProject( projectShortName )
            # check if successful
            if RamDaemonInterface.checkReply( projDict ):
                content = projDict['content']
                project = RamProject( projectName=content['name'], projectShortName=content['shortName'],
                                      projectPath=content['folder'], width=content['width'], height=content['height'],
                                      framerate=content['framerate'])

                return project

    def folderPath( self ): # Immutable #TODO if online
        if self._folderPath != '':
            return self._folderPath

        # TODO if online

        return self._folderPath

    def _getAssetsInFolder(self, folderPath, groupName='' ):
        """lists and returns all assets in the given folder"""
        foundFiles = os.listdir( folderPath )

        assetList = []
        
        for foundFile in foundFiles:
            # look in first 
            if os.path.isdir( folderPath + '/' + foundFile ):
                assets = self._getAssetsInFolder( folderPath + '/' + foundFile )
                assetList = assetList + assets
            else:
                # Try anyway
                asset = RamAsset.getFromPath( folderPath + '/' + foundFile )
                if asset is None:
                    continue
                if groupName == '' or asset.group() == groupName:
                    assetList.append( asset )

        return removeDuplicateObjectsFromList( assetList )

    def _getStepsInFolder(self, folderPath, stepType=StepType.ALL):
        pass
