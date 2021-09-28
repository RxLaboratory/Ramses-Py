# -*- coding: utf-8 -*-

#====================== BEGIN GPL LICENSE BLOCK ======================
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 3
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#======================= END GPL LICENSE BLOCK ========================

import os, re
from .file_info import RamFileInfo
from .daemon_interface import RamDaemonInterface
from .file_manager import RamFileManager
from .logger import log
from .ramses import Ramses
from .utils import escapeRegEx, removeDuplicateObjectsFromList
from .ram_settings import RamSettings
from .ram_object import RamObject
from .ram_asset import RamAsset
from .ram_shot import RamShot
from .ram_step import RamStep
from .ram_pipe import RamPipe
from .constants import StepType, FolderNames, ItemType

daemon = RamDaemonInterface.instance()
settings = RamSettings.instance()

class RamProject( RamObject ):
    """A project handled by Ramses. Projects contains general items, assets and shots."""

    @staticmethod
    def fromDict( projectDict ):
        """Builds a RamProject from dict like the ones returned by the RamDaemonInterface"""
        return RamProject(
            projectDict['name'],
            projectDict['shortName'],
            projectDict['folder'],
            projectDict['width'],
            projectDict['height'],
            projectDict['framerate']
        )

    @staticmethod
    def fromPath( path ):
        """Creates a project object from any path, trying to get info from the given path"""

        nm = RamFileInfo()
        nm.setFilePath( path )

        projectShortName = nm.project
        if projectShortName == '':
            return None

        projectPath = RamFileManager.getProjectFolder( path )
        return RamProject( "", projectShortName, projectPath )

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
        super(RamProject, self).__init__( projectName, projectShortName )
        self._folderPath = projectPath
        self._width = width
        self._height = height
        self._framerate = framerate
        # Cache
        self._adminPath = ''
        self._preProdPath = ''
        self._prodPath = ''
        self._postProdPath = ''
        self._assetsPath = {}
        self._shotsPath = ''
        self._exportPath = ''
        self._pipes = []

    def width( self ): #Mutable
        """
        Returns:
            int
        """

        if Ramses.instance().online():
            reply = daemon.getProject( self._shortName )
            # check if successful
            if RamDaemonInterface.checkReply( reply ):
                self._width = reply['content']['width']

        return self._width

    def height( self ): #Mutable
        """
        Returns:
            int
        """

        if Ramses.instance().online():
            reply = daemon.getProject( self._shortName )
            # check if successful
            if RamDaemonInterface.checkReply( reply ):
                self._height = reply['content']['height']

        return self._height

    def framerate( self ): #Mutable
        """
        Returns:
            float
        """

        if Ramses.instance().online():
            reply = daemon.getProject( self._shortName )
            # check if successful
            if RamDaemonInterface.checkReply( reply ):
                self._framerate = reply['content']['framerate']
                
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

    def adminPath( self ): #Immutable
        """Returns the path of the Admin folder (creates it if it does not exist yet)"""

        if self._adminPath != '':
            return self._adminPath

        projectFolder = self.folderPath()
        if not os.path.isdir( projectFolder ):
            return ''

        thePath = RamFileManager.buildPath((
            projectFolder,
            FolderNames.admin
        ))

        if not os.path.isdir( thePath ):
            os.makedirs( thePath )
        
        return thePath

    def preProdPath( self ): #Immutable
        """Returns the path of the PreProd folder (creates it if it does not exist yet)"""

        if self._preProdPath != '':
            return self._preProdPath

        projectFolder = self.folderPath()
        if not os.path.isdir( projectFolder ):
            return ''

        thePath = RamFileManager.buildPath((
            projectFolder,
            settings.folderNames.preProd
        ))

        if not os.path.isdir( thePath ):
            os.makedirs( thePath )

        return thePath

    def prodPath( self ): #Immutable
        """Returns the path of the Prod folder (creates it if it does not exist yet)"""

        if self._prodPath != '':
            return self._prodPath

        projectFolder = self.folderPath()
        if not os.path.isdir( projectFolder ):
            return ''

        thePath = RamFileManager.buildPath((
            projectFolder,
            settings.folderNames.prod
        ))

        if not os.path.isdir( thePath ):
            os.makedirs( thePath )

        return thePath

    def postProdPath( self ): #Immutable
        """Returns the path of the PostProd folder (creates it if it does not exist yet)"""

        if self._postProdPath != '':
            return self._postProdPath

        projectFolder = self.folderPath()
        if not os.path.isdir( projectFolder ):
            return ''

        thePath = RamFileManager.buildPath((
            projectFolder,
            settings.folderNames.postProd
        ))

        if not os.path.isdir( thePath ):
            os.makedirs( thePath )

        return thePath

    def assetsPath( self, assetGroup='' ): #Immutable
        """Returns the path of the Assets folder (creates it if it does not exist yet)"""

        groupKey = 'ramsesAssetsPath'
        if assetGroup != '':
            groupKey = assetGroup

        if groupKey in self._assetsPath:
            if self._assetsPath[groupKey] != '':
                return self._assetsPath[groupKey]

        projectFolder = self.folderPath()
        if not os.path.isdir( projectFolder ):
            return ''

        thePath = RamFileManager.buildPath((
            projectFolder,
            settings.folderNames.assets,
            assetGroup
        ))

        if not os.path.isdir( thePath ):
            os.makedirs( thePath )

        self._assetsPath[groupKey] = thePath
        
        return thePath

    def shotsPath( self ): #Immutable
        """Returns the path of the Shots folder (creates it if it does not exist yet)"""

        if self._shotsPath != '':
            return self._shotsPath

        projectFolder = self.folderPath()
        if not os.path.isdir( projectFolder ):
            return ''

        thePath = RamFileManager.buildPath((
            projectFolder,
            settings.folderNames.shots
        ))

        if not os.path.isdir( thePath ):
            os.makedirs( thePath )
        
        return thePath

    def exportPath( self ): #Immutable
        """Returns the path of the Export folder (creates it if it does not exist yet)"""

        if self._exportPath != '':
            return self._exportPath

        projectFolder = self.folderPath()
        if not os.path.isdir( projectFolder ):
            return ''

        thePath = RamFileManager.buildPath((
            projectFolder,
            settings.folderNames.export
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

        # If we're online, ask the client (return a dict)
        if Ramses.instance().online():
            reply = daemon.getAsset( assetShortName )
            # check if successful
            if RamDaemonInterface.checkReply( reply ):
                content = reply['content']
                return RamAsset.fromDict( content )

        # Else, check in the folders
        for asset in self._getAssetsInFolder( self.assetsPath() ):
            if asset.shortName() == assetShortName:
                return asset

        return None

    def assets( self, groupName="" ): # Mutable
        """Available assets in this project and group.
        If groupName is an empty string, returns all assets.

        Args:
            groupName (str, optional): Defaults to "".

        Returns:
            list of RamAsset
        """

        assetsList = []

        # If we're online, ask the client (return a dict)
        if Ramses.instance().online():
            reply = daemon.getAssets()
            # check if successful
            if RamDaemonInterface.checkReply( reply ):
                content = reply['content']
                foundAssets = content['assets']
                for assetDict in foundAssets:
                    if groupName == "" or assetDict['group'] == groupName:
                        asset = RamAsset.fromDict( assetDict )
                        assetsList.append( asset )
                if len(assetsList) > 0:
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
            reply = daemon.getAssetGroups()
            # check if successful
            if RamDaemonInterface.checkReply( reply ):
                content = reply['content']
                foundGroups = content['assetGroups']
                for group in foundGroups:
                    groupName = group['name']
                    assetGroups.append(groupName)
                return assetGroups

        # Else check in the folders
        assetsFolderPath = self.assetsPath()

        if assetsFolderPath == '':
            return assetGroups

        foundFiles = os.listdir( assetsFolderPath )

        for foundFile in foundFiles:
            if not os.path.isdir( assetsFolderPath + '/' + foundFile ):
                continue
            if RamFileManager._isRamsesItemFoldername( foundFile ):
                continue
            assetGroups.append( foundFile )

        return assetGroups

    def shot( self, shotShortName ):
        """Gets a shot with its short name.

        Args:
            shotShortName (str): the shortname

        Returns:
            RamShot
        """

        # If we're online, ask the client (return a dict)
        if Ramses.instance().online():
            reply = daemon.getShot( shotShortName )
            # check if successful
            if RamDaemonInterface.checkReply( reply ):
                content = reply['content']
                return RamShot.fromDict( content )

        # Else, check in the folders
        shotsFolderPath = self.shotsPath()
        if shotsFolderPath == '':
            return None

        for shotFolder in os.listdir( shotsFolderPath ):
            nm = RamFileInfo()
            nm.setFileName( shotFolder )
            if nm.shortName == shotShortName:
                return RamShot.fromPath( shotsFolderPath + "/" + shotFolder )

    def shots( self, nameFilter = "*", sequence = "" ):
        """Available shots in this project

        Args:
            nameFilter

        Returns:
            list of RamShot
        """

        shotsList = []

        #Preparing regex for wildcards
        useFilter = not nameFilter in ("", "*")
        if useFilter: 
            nameFilter = escapeRegEx( nameFilter )
            nameFilter = nameFilter.replace( '\\*', '([a-zA-Z0-9+-]{1,10})?' )
            regex = re.compile( nameFilter, re.IGNORECASE )

        # If we're online, ask the client (return a dict)
        if Ramses.instance().online():
            reply = daemon.getShots()
            # check if successful
            if RamDaemonInterface.checkReply( reply ):
                foundShots = reply['content']['shots']
                for shotDict in foundShots:
                    if useFilter:
                        if not re.match(regex, shotDict['shortName']):
                            continue
                    if sequence == "" or shotDict['sequence'] == sequence:
                        shot = RamShot.fromDict( shotDict )
                        if shot is not None:
                            shotsList.append( shot )

                if len(shotsList) > 0:
                    return shotsList

        # Else check in the folders
        shotsFolderPath = self.shotsPath()
        if shotsFolderPath == '':
            return shotsList
       
        foundShots = []

        for foundFile in os.listdir( shotsFolderPath ):
            foundShotPath = shotsFolderPath + '/' + foundFile
            if not os.path.isdir( foundShotPath ):
                continue
            if not RamFileManager._isRamsesItemFoldername( foundFile ):
                continue
            if not foundFile.split('_')[1] == ItemType.SHOT:
                continue

            foundShotName = foundFile.split('_')[2]
            
            if useFilter:
                if not re.match( regex, foundShotName ):
                    continue
            shot = RamShot.fromPath( foundShotPath )
            if shot is not None:
                foundShots.append( shot )

        return foundShots

    def sequences( self ): # Mutable
        sequences = []

        # If we're online, ask the client
        if Ramses.instance().online():
            reply = daemon.getSequences()
            # check if successful
            if RamDaemonInterface.checkReply( reply ):
                content = reply['content']
                foundGroups = content['sequences']
                for group in foundGroups:
                    groupName = group['name']
                    sequences.append(groupName)
        
        return sequences

    # itemType is undocumented: used internally by RamStep.fromPath to improve performance
    def step( self, stepShortName, itemType='' ):
        """Gets a step with its short name.

        Args:
            stepShortName (str): the shortname

        Returns:
            RamStep
        """
        # If we're online, ask the client (return a dict)
        if Ramses.instance().online():
            reply = daemon.getStep( stepShortName )
            # check if successful
            if RamDaemonInterface.checkReply( reply ):
                return RamStep.fromDict( reply['content'] )

        # Build the step folder name to find it
        nm = RamFileInfo()
        nm.project = self.shortName()
        nm.step = stepShortName
        nm.ramType = ItemType.GENERAL
        stepFolderName = nm.fileName()

        # Check in Pre Prod
        stepFolderPath = RamFileManager.buildPath((
            self.preProdPath(),
            stepFolderName
            ))
        if os.path.isdir( stepFolderPath ):
            return RamStep(
                    "",
                    stepShortName,
                    stepFolderPath,
                    StepType.PRE_PRODUCTION
                )

        # Check in Post Prod
        stepFolderPath = RamFileManager.buildPath((
            self.postProdPath(),
            stepFolderName
            ))
        if os.path.isdir( stepFolderPath ):
            return RamStep(
                    "",
                    stepShortName,
                    stepFolderPath,
                    StepType.POST_PRODUCTION
                )

        # Check in prod
        stepFolderPath = RamFileManager.buildPath((
            self.prodPath(),
            stepFolderName
            ))

        # If we've got the folder and we already know the type, return
        if os.path.isdir( stepFolderPath ) and itemType != '' and itemType != 'G':
            if itemType == ItemType.ASSET:
                return RamStep(
                    "",
                    stepShortName,
                    stepFolderPath,
                    StepType.ASSET_PRODUCTION
                )
            elif itemType == ItemType.SHOT:
                return RamStep(
                    "",
                    stepShortName,
                    stepFolderPath,
                    StepType.SHOT_PRODUCTION
                )

        # Try to find the type in the assets
        if RamFileManager.isAssetStep( stepShortName, self.assetsPath() ):
            return RamStep(
                "",
                stepShortName,
                stepFolderPath,
                StepType.ASSET_PRODUCTION
            )

        # Try to find it in the shots
        if RamFileManager.isShotStep( stepShortName, self.shotsPath() ):
            return RamStep(
                "",
                stepShortName,
                stepFolderPath,
                StepType.SHOT_PRODUCTION
            )

        # Not found, just return as a general production step
        if os.path.isdir( stepFolderPath ):
            return RamStep(
                "",
                stepShortName,
                stepFolderPath,
                StepType.PRODUCTION
            )

        return None
        
    def steps( self, stepType=StepType.ALL, deepSearch=False ): # Mutable
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
            reply = daemon.getSteps()
            # check if successful
            if RamDaemonInterface.checkReply( reply ):
                content = reply['content']
                foundSteps = content['steps']
                for stepDict in foundSteps:
                    ok = False
                    foundType = stepDict['type']
                    if stepType == foundType:
                        ok = True
                    elif stepType == StepType.ALL or foundType == StepType.ALL:
                        ok = True
                    elif stepType == StepType.PRODUCTION:
                        if foundType == StepType.SHOT_PRODUCTION or foundType == StepType.ASSET_PRODUCTION:
                            ok = True
                    elif foundType == StepType.PRODUCTION:
                        if stepType == StepType.SHOT_PRODUCTION or stepType == StepType.ASSET_PRODUCTION:
                            ok = True
                    if not ok:
                        continue
                    stepsList.append( RamStep.fromDict( stepDict ) )
                if len(stepsList) > 0:
                    return stepsList
                
        # Else, check in the folders

        # Check StepType: Pre-Prod
        if stepType == StepType.PRE_PRODUCTION or stepType ==  StepType.ALL:
            stepsFolderPath = self.preProdPath()

            if stepsFolderPath != '':
                for preProdFile in os.listdir( stepsFolderPath ):
                    # we keep only the folders
                    preProdFolder = stepsFolderPath + "/" + preProdFile
                    if not os.path.isdir( preProdFolder ):
                        continue
                    step = RamStep.fromPath( preProdFolder )
                    if step is None:
                        continue
                    stepsList.append( step )

            if stepType == StepType.PRE_PRODUCTION:
                return stepsList
        
        # Check StepType: Prod (assets + shots)
        if stepType == StepType.PRODUCTION or stepType == StepType.ALL or stepType == StepType.SHOT_PRODUCTION or stepType == StepType.ASSET_PRODUCTION:
            stepsFolderPath = self.prodPath()
            if stepsFolderPath != '':
                for prodFile in os.listdir( stepsFolderPath ):
                    # we keep only the folders
                    prodFolder = stepsFolderPath + "/" + prodFile
                    if not os.path.isdir( prodFolder ):
                        continue

                    step = RamStep.fromPath(prodFolder, self)

                    if step is None:
                        continue
                    foundType = step.stepType()
                    ok = False
                    if stepType == foundType:
                        ok = True
                    elif stepType == StepType.ALL or foundType == StepType.ALL:
                        ok = True
                    elif stepType == StepType.PRODUCTION:
                        if foundType == StepType.SHOT_PRODUCTION or foundType == StepType.ASSET_PRODUCTION:
                            ok = True
                    elif foundType == StepType.PRODUCTION:
                        if stepType == StepType.SHOT_PRODUCTION or stepType == StepType.ASSET_PRODUCTION:
                            ok = True
                    if not ok:
                        continue

                    if not step in stepsList:
                        stepsList.append( step )
            
            # Check in Assets and Shots
            # If deepSearch only, because this can take a lot of time!
            if deepSearch:
                if stepType == StepType.ALL or stepType == StepType.PRODUCTION or stepType == StepType.ASSET_PRODUCTION:
                    assetsPath = self.assetsPath()
                    if assetsPath !='':
                        for groupName in os.listdir( assetsPath ):
                            groupFolder = assetsPath + "/" + groupName
                            if not os.path.isdir( groupFolder ):
                                continue

                            for assetFolderName in os.listdir(groupFolder):
                                assetFolder = groupFolder + "/" + assetFolderName
                                if not os.path.isdir( assetFolder ):
                                    continue
                                for stepFolderName in os.listdir(assetFolder):
                                    stepFolder = assetFolder + "/" + stepFolderName
                                    if not os.path.isdir( stepFolder ):
                                        continue
                                    step = RamStep.fromPath( stepFolder )
                                    if step is None:
                                        continue
                                    if not step in stepsList:
                                        stepsList.append( step )

                if stepType == StepType.ALL or stepType == StepType.PRODUCTION or stepType == StepType.SHOT_PRODUCTION:
                    shotsPath = self.shotsPath()
                    if shotsPath != '':
                        for shotName in os.listdir( shotsPath ):
                            shotFolder = shotsPath + "/" + shotName
                            if not os.path.isdir( shotFolder ):
                                continue
                            for stepFolderName in os.listdir( shotFolder ):
                                stepFolder = shotFolder + "/" + stepFolderName
                                if not os.path.isdir( stepFolder ):
                                    continue
                                step = RamStep.fromPath( stepFolder )
                                if step is None:
                                    continue
                                if not step in stepsList:
                                    stepsList.append( step )

        # Check StepType: Post-Prod
        if stepType == StepType.POST_PRODUCTION or stepType == StepType.ALL:
            stepsFolderPath = self.postProdPath()

            if stepsFolderPath != '':
                for postProdFile in os.listdir( stepsFolderPath ):
                    # we keep only the folders
                    postProdFolder = stepsFolderPath + "/" + postProdFile
                    if not os.path.isdir( postProdFolder ):
                        continue
                    step = RamStep.fromPath( postProdFolder )
                    if step is None:
                        continue
                    stepsList.append( step )

            if stepType == StepType.POST_PRODUCTION:
                return stepsList

        return stepsList

    def pipes( self ): #immutable
        """Available pipes in this project

        Returns:
            list of RamPipe
        """

        if len(self._pipes) > 0:
            return self._pipes

        # If we're online, ask the client
        # DEV let's do it every time, just waiting for the implementation on the client side
        #if Ramses.instance().online():
        reply = daemon.getPipes()
        # check if successful
        if RamDaemonInterface.checkReply( reply ):
            pipesDict = reply['content']['pipes']
            for pipeDict in pipesDict:
                self._pipes.append(
                    RamPipe.fromDict( pipeDict )
                )
        
        # note: any way to define pipes offline ?

        return self._pipes

    def folderPath( self ): # Immutable
        if self._folderPath != '':
            return self._folderPath

        if Ramses.instance().online():
            reply = daemon.getProject( self.shortName() )
            # check if successful
            if RamDaemonInterface.checkReply( reply ):
                self._folderPath = reply['content']['folder']

        return self._folderPath

    def _getAssetsInFolder(self, folderPath, groupName='' ):
        """lists and returns all assets in the given folder"""
        assetList = []
        
        for foundFile in os.listdir( folderPath ):
            # look in subfolder
            if os.path.isdir( folderPath + '/' + foundFile ):
                assets = self._getAssetsInFolder( folderPath + '/' + foundFile, groupName )
                assetList = assetList + assets
            
            # Get Asset
            asset = RamAsset.fromPath( folderPath + '/' + foundFile )
            if asset is None:
                continue
            if groupName == '' or asset.group() == groupName:
                assetList.append( asset )

        return removeDuplicateObjectsFromList( assetList )
