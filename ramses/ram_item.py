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

import os
from platform import version
from .file_info import RamFileInfo
from .ramses import Ramses
from .ram_object import RamObject
from .file_manager import RamFileManager
from .daemon_interface import RamDaemonInterface
from .logger import log
from .constants import Log, LogLevel, ItemType, FolderNames

# Keep the daemon at hand
daemon = RamDaemonInterface.instance()

class RamItem( RamObject ):
    """
    Base class for RamAsset and RamShot.
    An item of the project, either an asset or a shot.
    """

    @staticmethod
    def fromPath( fileOrFolderPath ):
        from .ram_shot import RamShot
        from .ram_asset import RamAsset
        """Returns a RamAsset or RamShot instance built using the given path.
        The path can be any file or folder path from the asset 
        (a version file, a preview file, etc)

        Args:
            path (str)

        Returns:
            RamAsset or RamShot
        """

        # Get info from the path
        nm = RamFileInfo()
        nm.setFilePath( fileOrFolderPath )
        if nm.project == '': # Wrong name, we can't do anything more
            log (Log.MalformedName, LogLevel.Debug)
            return None

        # Try to find the folder
        saveFilePath = RamFileManager.getSaveFilePath( fileOrFolderPath )
        if saveFilePath == "":
            log( Log.PathNotFound, LogLevel.Critical )
            return None

        saveFolder = os.path.dirname( saveFilePath )
        itemFolder = saveFolder
        itemFolderName = os.path.basename( itemFolder )

        if not RamFileManager._isRamsesItemFoldername( itemFolderName ): # We're probably in a step subfolder
            itemFolder = os.path.dirname( saveFolder )
            itemFolderName = os.path.basename( itemFolder )
            if not RamFileManager._isRamsesItemFoldername( itemFolderName ): # Still wrong: consider it's a general item 
                return RamItem(
                    nm.project,
                    nm.step,
                    saveFolder,
                    ItemType.GENERAL
                )

        if nm.ramType == ItemType.ASSET: 
            # Get the group name
            assetGroupFolder = os.path.dirname( itemFolder )
            assetGroup = os.path.basename( assetGroupFolder )
            return RamAsset(
                '',
                nm.shortName,
                itemFolder,
                assetGroup
            )

        if nm.ramType == ItemType.SHOT:
            return RamShot(
                '',
                nm.shortName,
                itemFolder,
                0.0
            )

        if nm.ramType == ItemType.GENERAL:
            return RamItem(
                nm.shortName,
                nm.step,
                saveFolder,
                ItemType.GENERAL
            )

        log( "The given path does not belong to a shot nor an asset", LogLevel.Debug )
        return None

    # Do not document Asset Group nor Type as its used by derived classes
    def __init__( self, itemName, itemShortName, itemFolder="", itemType=ItemType.GENERAL, assetGroup="" ):
        """
        Args:
            itemName (str)
            itemShortName (str)
            itemFolder (str, optional): Defaults to "".
        """
        super(RamItem, self).__init__( itemName, itemShortName )
        self._folderPath = itemFolder
        self._itemType = itemType
        self._group = assetGroup
        self._project = None
        self._projectShortName = ""

    def __updateFromDaemon(self):
        """Updates all info from what we get from the daemon"""

        if not Ramses.instance().online():
            return None

        if self._itemType == ItemType.SHOT:
            replyDict = daemon.getShot( self._shortName, self._name )
            # check if successful
            if daemon.checkReply( replyDict ):
                self._folderPath = replyDict['content']['folder']
                self._name = replyDict['content']['name']
                return replyDict
                
        replyDict = daemon.getAsset( self._shortName, self._name )
        # check if successful
        if daemon.checkReply( replyDict ):
            self._folderPath = replyDict['content']['folder']
            self._name = replyDict['content']['name']
            self._group = replyDict['content']['group']
            return replyDict

        return None
                
    def currentStatus( self, step="", resource="" ):
        """The current status for the given step

        Args:
            step (RamStep or str): The step.
            resource (str, optional): The name of the resource. Defaults to "".

        Returns:
            RamStatus
        """

        from .ram_status import RamStatus

        # Check step, return shortName (str) or "" or raise TypeError:
        step = RamObject.getObjectShortName( step )
        if step == "":
            return RamStatus(Ramses.instance().defaultState)

        # If we're online, ask the client (return a dict)
        if Ramses.instance().online():
            replyDict = daemon.getCurrentStatus( self._shortName, self._name, step, self._itemType )
            # check if successful
            print(replyDict)
            if daemon.checkReply( replyDict ):
                return RamStatus.fromDict( replyDict['content'] )
                
        # If offline
        currentVersionPath = self.latestVersionFilePath( resource, '', step )
        if currentVersionPath == "":
            log( "There was an error getting the latest version or none was found." )
            return None

        return RamStatus.fromPath( currentVersionPath )

    # Override from RamObject to get from Daemon
    def name( self ):
        """
        Returns:
            str
        """
        if self._name != '':
            return self._name

        # If we're online, ask the client (return a dict)
        self.__updateFromDaemon()

        return self._name

    # Do not document "assetGroup" argument, it should stay hidden
    # (just automatically passed by RamAsset.folderPath())
    def folderPath( self ):
        """The absolute path to the folder containing the item, or to the step subfolder if provided

        Args:
            step (RamStep or str, optional): Defaults to "".

        Returns:
            str
        """

        if self._folderPath != '':
            return self._folderPath

        # If we're online, ask the client
        self.__updateFromDaemon()

        if self._folderPath != '':
            return self._folderPath

        # Project
        project = Ramses.instance().currentProject()
        if project is None:
            return ""

        nm = RamFileInfo()
        nm.project = project.shortName()
        nm.step = self.shortName()
        nm.ramType = self.itemType()
        itemFolderName = nm.fileName()

        if self._itemType == ItemType.SHOT:
            # Get the shot folder name
            self._folderPath = RamFileManager.buildPath((
                project.shotsPath(),
                itemFolderName
            ))
            
            return self._folderPath
            
        if self._itemType == ItemType.ASSET:
            # add the group
            self._folderPath = RamFileManager.buildPath((
                    project.assetsPath(),
                    self.group(),
                    itemFolderName
                ))

            return self._folderPath
            
        return ""

    def stepFolderPath(self, step=""):
        # Check step, return shortName (str) or "" or raise TypeError:
        step = RamObject.getObjectShortName( step )

        folderPath = self.folderPath()
        if folderPath == "" or step == "" or self.itemType() == ItemType.GENERAL:
            return folderPath

        project = self.projectShortName()

        nm = RamFileInfo()
        nm.project = project
        nm.step = step
        nm.ramType = self.itemType()
        nm.shortName = self.shortName()
        stepFolderName = nm.fileName()

        stepFolderPath = RamFileManager.buildPath((
            folderPath,
            stepFolderName
        ))

        if not os.path.isdir(stepFolderPath):
            os.makedirs( stepFolderPath )

        return stepFolderPath

    def stepFilePaths( self, step="" ):
        """Returns the step files"""
        step = RamObject.getObjectShortName( step )

        stepFolder = self.stepFolderPath(step)
        if stepFolder == '':
            return []
        
        pShortName = self.projectShortName()
        if pShortName == '':
            return []

        files = []

        for file in os.listdir(stepFolder):
            # check file
            nm = RamFileInfo()
            if not nm.setFileName( file ):
                continue
            if nm.project != pShortName or nm.step != step or nm.shortName != self.shortName() or nm.ramType != self.itemType():
                continue
            files.append(RamFileManager.buildPath((
                stepFolder,
                file
            )))
        return files

    def stepFilePath(self, resource="", extension="", step="", ):
        """Returns a specific step file"""
        step = RamObject.getObjectShortName( step )

        stepFolder = self.stepFolderPath(step)
        if stepFolder == '':
            return ''

        pShortName = self.projectShortName()
        if pShortName == '':
            return ''

        nm = RamFileInfo()
        nm.project = pShortName
        nm.step = step
        nm.extension = extension
        nm.ramType = self.itemType()
        nm.shortName = self.shortName()
        nm.resource = resource

        fileName = nm.fileName()

        filePath = RamFileManager.buildPath((
            stepFolder,
            fileName
        ))
        if os.path.isfile(filePath):
            return filePath
        return ""

    def latestVersion( self, resource="", state="", step=""):
        """Returns the highest version number for the given state (wip, pub…) (or all states if empty string).

        Args:
            step (RamStep or str)
            resource (str, optional): Defaults to "".
            stateId (str, optional): Defaults to "wip".

        Returns:
            int
        """

        state = RamObject.getObjectShortName(state)
        step = RamObject.getObjectShortName(step)

        highestVersion = -1
       
        versionFolder = self.versionFolderPath( step )
        if versionFolder == '':
            return highestVersion

        for file in os.listdir( versionFolder ):
            nm = RamFileInfo()
            if not nm.setFileName( file ):
                continue
            if nm.step != step and step != '':
                continue
            if nm.resource == resource:
                if nm.state == state or state == "":
                    if nm.version > highestVersion:
                        highestVersion = nm.version

        return highestVersion
        
    def previewFolderPath( self, step="" ):
        """Gets the path to the preview folder.
            Paths are relative to the root of the item folder.

        Args:
            step (RamStep or str)

        Returns:
            str
        """
        # Check step, return shortName (str) or "" or raise TypeError:
        stepFolder = self.stepFolderPath(step )

        if stepFolder == '':
            return ''

        previewFolder = RamFileManager.buildPath(( 
            stepFolder,
            FolderNames.preview
            ))

        if not os.path.isdir(previewFolder):
            os.makedirs(previewFolder)

        return previewFolder

    def previewFilePaths( self, resource="", step=""):
        """Gets the list of file paths in the preview folder.
            Paths are relative to the root of the item folder.

        Args:
            step (RamStep or str)
            resource (str, optional): Defaults to "".

        Returns:
            list of str
        """

        previewFolderPath = self.previewFolderPath(step)

        return RamFileManager.getFileWithResource( previewFolderPath, resource)

    def publishFolderPath( self, step=""): 
        """Gets the path to the publish folder.
        Paths are relative to the root of the item folder.

        Args:
            step (RamStep or str)   

        Returns:
            str
        """
        # Check step, return shortName (str) or "" or raise TypeError:
        stepFolder = self.stepFolderPath(step )

        if stepFolder == '':
            return ''

        publishFolder = RamFileManager.buildPath(( 
            stepFolder,
            FolderNames.publish
            ))

        if not os.path.isdir(publishFolder):
            os.makedirs(publishFolder)

        return publishFolder

    def publishedVersionFolderPaths( self, step="" ):
        """Gets the list of file paths in the publish folder.
            Paths are relative to the root of the item folder.

        Args:
            step (RamStep or str)
            resource (str, optional): Defaults to "".

        Returns:
            list of str
        """

        publishFolderPath = self.publishFolderPath(step)
        versionFolders = []
        for f in os.listdir(publishFolderPath):
            folderPath = RamFileManager.buildPath(( publishFolderPath, f ))
            if not os.path.isdir(folderPath): continue
            versionFolders.append( folderPath )

        versionFolders.sort(key=RamFileManager._publishVersionFoldersSorter)

        return versionFolders

    def latestPublishedVersion( self, fileName='', resource='' ):
        """Gets the latest published version for the given fileName. Returns the latest folder if the fileName is omitted or an empty string"""
        versionFolders = self.publishedVersionFolderPaths()
        
        if len(versionFolders) == 0: return ''

        for folder in versionFolders:
            # Check the resource
            folderName = os.path.dirname( folder ).split('_')
            if len(folderName) != 3 and resource != '': continue
            elif len(folderName) == 3 and resource != folderName[0]: continue
            
            if fileName == '': return folder

            for f in os.listdir(folder):
                if f == fileName: return RamFileManager.buildPath((folder, f))

    def versionFolderPath( self, step="" ): 
        """Path to the version folder relative to the item root folder

        Args:
            step (RamStep)

        Returns:
            str
        """
        # Check step, return shortName (str) or "" or raise TypeError:
        stepFolder = self.stepFolderPath( step )

        if stepFolder == '':
            return ''

        versionFolder = RamFileManager.buildPath(( 
            stepFolder,
            FolderNames.versions
            ))

        if not os.path.isdir(versionFolder):
            os.makedirs( versionFolder )
        
        return versionFolder

    def latestVersionFilePath( self, resource="", state="", step="" ):
        """Latest version file path

        Args:
            step (RamStep or str)
            resource (str, optional): Defaults to "".

        Returns:
            str
        """

        step = RamObject.getObjectShortName(step)

        versionFolderPath = self.versionFolderPath(step )

        if versionFolderPath == '':
            return ''

        versionFile = ''
        highestVersion = -1

        for file in os.listdir( versionFolderPath ):
            nm = RamFileInfo()
            if not nm.setFileName( file ):
                continue
            if nm.step != step and step != '':
                continue
            if nm.resource == resource:
                if nm.state == state or state == '':
                    if nm.version > highestVersion:
                        highestVersion = nm.version
                        versionFile = RamFileManager.buildPath((
                            versionFolderPath,
                            file
                        ))

        return versionFile

    def versionFilePaths( self, resource="", step="" ):
        """Gets all version files for the given resource"""

        step = RamObject.getObjectShortName( step )

        versionFolderPath = self.versionFolderPath(step )

        if versionFolderPath == '':
            return ''

        pShortName = self.projectShortName()
        if pShortName == '':
            return []

        files = []

        for file in os.listdir( versionFolderPath ):
            nm = RamFileInfo()
            if not nm.setFileName( file ):
                continue
            if nm.project != pShortName:
                continue
            itemType = self.itemType()
            if nm.ramType != itemType:
                continue
            if itemType == ItemType.GENERAL:
                if nm.step != self.shortName():
                    continue
                if self.name() != nm.shortName:
                    continue
            else:
                if nm.step != step or nm.shortName != self.shortName():
                    continue
            if nm.resource == resource:
                files.append(RamFileManager.buildPath((
                    versionFolderPath,
                    file
                )))

        files.sort( key = RamFileManager._versionFilesSorter )
        return files

    def isPublished( self, step="" ):
        """Convenience function to check if there are published files in the publish folder.
            Equivalent to len(self.publishedVersionFolderPaths(step, resource)) > 0

        Args:
            step (RamStep)
            resource (str, optional): Defaults to "".

        Returns:
            bool
        """
        result = self.publishedVersionFolderPaths( step )
        return len( result ) > 0

    def setStatus( self, status, step ):
        """Sets the current status for the given step

        Args:
            status (RamStatus)
            step (RamStep)
        """
        # Check step, return shortName (str) or "" or raise TypeError:
        step = RamObject.getObjectShortName( step )

        if not Ramses.instance().online():
            return

        if self.itemType() == ItemType.GENERAL:
            return

        step = RamObject.getObjectShortName( step )
        if step == "":
            return

        daemon.setStatus(
            self.shortName(),
            self.name(),
            step,
            self.itemType(),
            status.state.shortName(),
            status.comment,
            status.completionRatio,
            status.version,
            status.published,
            status.user
        )    

    def status(self, step): #TODO
        """Gets the current status for the given step"""
        pass

    def itemType( self ):
        """Returns the type of the item"""
        return self._itemType

    def steps( self ):
        """Returns the steps used by this asset"""
        assetGroup = self.group()

        project = self.project()
        if project is None:
            return []

        stepsList = []

        # If we're online, ask the client (return a dict)
        if Ramses.instance().online():
            replyDict = daemon.getCurrentStatuses( self._shortName, self._name, self._itemType )
            # check if successful
            if RamDaemonInterface.checkReply( replyDict ):
                content = replyDict['content']
                statusList = content['status']
                for status in statusList:
                    step = project.step(status['step'] )
                    if step is not None:
                        stepsList.append( step )

                if len(stepsList) > 0:
                    return stepsList

        # Else check in the folder
        folder = self.folderPath( assetGroup )
        if folder == '':
            return

        for f in folder:
            nm = RamFileInfo()
            nm.setFileName( f )
            if nm.step != "":
                step = project.step( nm.step )
                if step is not None:
                    stepsList.append( step )

        return stepsList

    def project(self): # Immutable
        """Returns the project this item belongs to"""
        from .ram_project import RamProject

        if self._project is not None:
            return self._project

        folderPath = self.folderPath()
        if folderPath == '':
            return None

        self._project = RamProject.fromPath( folderPath )
        return self._project

    def projectShortName(self): # Immutable
        """Returns the short name of the project this item belongs to"""

        if self._projectShortName != "":
            return self._projectShortName

        if self._project is not None:
            self._projectShortName = self._project.shortName()
            return self._projectShortName

        folderPath = self.folderPath()
        if folderPath == '':
            return self._projectShortName

        nm = RamFileInfo()
        nm.setFilePath( folderPath )
        if nm.project == '':
            return self._projectShortName

        self._projectShortName = nm.project
        return self._projectShortName

    # Documented in RamAsset only
    def group( self ): # Immutable
        """The name of group containing this asset. (e.g. Props)

        Returns:
            str
        """

        if not self.itemType() == ItemType.ASSET:
            return ""

        if self._group != "":
            return self._group

        # If we're online, ask the client
        self.__updateFromDaemon()

        if self._group != "":
            return self._group

        # Else, check in the folders
        folderPath = self.folderPath()

        if not os.path.isdir( folderPath ):
            log( Log.PathNotFound + " " + folderPath, LogLevel.Critical )
            return self._group

        parentFolder = os.path.dirname( folderPath )
        parentFolderName = os.path.basename( parentFolder )

        if parentFolderName != FolderNames.assets:
            self._group = parentFolderName
        else:
            self._group = ''
            
        return self._group