# -*- coding: utf-8 -*-

import os
from platform import version

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
        pathInfo = RamFileManager.decomposeRamsesFilePath( fileOrFolderPath )
        if not pathInfo: # Wrong name, we can't do anything more
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
                    pathInfo['resource'],
                    pathInfo['object'],
                    saveFolder,
                    ItemType.GENERAL,
                    pathInfo['project']
                )

        if pathInfo['type'] == ItemType.ASSET: 
            # Get the group name
            assetGroupFolder = os.path.dirname( itemFolder )
            assetGroup = os.path.basename( assetGroupFolder )
            return RamAsset(
                '',
                pathInfo['object'],
                itemFolder,
                assetGroup
            )

        if pathInfo['type'] == ItemType.SHOT:
            return RamShot(
                '',
                pathInfo['object'],
                itemFolder,
                0.0
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

        # If we're online, ask the client (return a dict)
        if Ramses.instance().online():
            replyDict = daemon.getCurrentStatus( self._shortName, self._name, step )
            # check if successful
            if daemon.checkReply( replyDict ):
                return RamStatus.fromDict( replyDict['content'] )
                
        # If offline
        currentVersionPath = self.latestVersionFilePath( resource, '', step )
        if currentVersionPath == "":
            log( "There was an error getting the latest version or none was found." )
            return None

        return RamStatus.fromPath( currentVersionPath )

    # Do not document "assetGroup" argument, it should stay hidden
    # (just automatically passed by RamAsset.folderPath())
    def folderPath( self ):
        """The absolute path to the folder containing the item, or to the step subfolder if provided

        Args:
            step (RamStep or str, optional): Defaults to "".

        Returns:
            str
        """

        if self._folderPath != "":
            return self._folderPath

        # If we're online, ask the client (return a dict)
        if Ramses.instance().online():
            if self._itemType == ItemType.SHOT:
                replyDict = daemon.getShot( self._shortName, self._name )
                # check if successful
                if daemon.checkReply( replyDict ):
                    return replyDict['content']['folder']
            elif self._itemType == ItemType.ASSET:
                replyDict = daemon.getAsset(( self._shortName, self._name ))
                # check if successful
                if daemon.checkReply( replyDict ):
                    return replyDict['content']['folder']

        # Project
        project = Ramses.instance().currentProject()
        if project is None:
            return ""

        itemFolderName = RamFileManager.buildRamsesFileName(
            project.shortName(),
            self.shortName(),
            '',
            self.itemType()
        )

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
        if folderPath == "":
            return ""

        if step == "":
            return folderPath

        pathInfo = RamFileManager.decomposeRamsesFilePath( folderPath )
        if pathInfo is None:
            return ""

        project = pathInfo['project']

        stepFolderName = RamFileManager.buildRamsesFileName(
            project,
            step,
            '',
            self.itemType(),
            self.shortName()
        )

        return RamFileManager.buildPath((
            folderPath,
            stepFolderName
        ))

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

        highestVersion = -1
       
        versionFolder = self.versionFolderPath( step )
        if versionFolder == '':
            return highestVersion

        for file in os.listdir( versionFolder ):
            fileInfo = RamFileManager.decomposeRamsesFileName(file)
            if fileInfo['resource'] == resource:
                if fileInfo['state'] == state or state == "":
                    if fileInfo['version'] > highestVersion:
                        highestVersion = fileInfo['version']

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

        return RamFileManager.buildPath(( 
            stepFolder,
            FolderNames.preview
            ))

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

        return RamFileManager.buildPath(( 
            stepFolder,
            FolderNames.publish
            ))

    def publishFilePaths( self, resource="", step="" ):
        """Gets the list of file paths in the publish folder.
            Paths are relative to the root of the item folder.

        Args:
            step (RamStep or str)
            resource (str, optional): Defaults to "".

        Returns:
            list of str
        """

        publishFolderPath = self.publishFolderPath(step)
        return RamFileManager.getFileWithResource( publishFolderPath, resource)

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
        versionFolderPath = self.versionFolderPath(step )

        if versionFolderPath == '':
            return ''

        versionFile = ''
        highestVersion = -1

        for file in os.listdir( versionFolderPath ):
            fileInfo = RamFileManager.decomposeRamsesFileName( file )
            if fileInfo['resource'] == resource:
                if fileInfo['state'] == state or state == '':
                    if fileInfo['version'] > highestVersion:
                        highestVersion = fileInfo['version']
                        versionFile = RamFileManager.buildPath((
                            versionFolderPath,
                            file
                        ))

        return versionFile

    def isPublished( self, resource="", step="" ):
        """Convenience function to check if there are published files in the publish folder.
            Equivalent to len(self.publishedFilePaths(step, resource)) > 0

        Args:
            step (RamStep)
            resource (str, optional): Defaults to "".

        Returns:
            bool
        """
        result = self.publishFilePaths( step, resource, step )
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

        daemon.setStatus(
            self.shortName(),
            self.name(),
            step,
            self.itemType(),
            status.state.shortName(),
            status.comment,
            status.completionRatio,
            status.version,
            status.user,
            status.stateDate
        )    

    def status(self, step): #TODO
        """Gets the current status for the given step"""
        pass

    def itemType( self ):
        """Returns the type of the item"""
        return self._itemType

    def steps( self ):
        """Returns the steps used by this asset"""

        from .ram_project import RamProject

        assetGroup = self.group()

        project = Ramses.instance().currentProject()
        if project is None:
            project = RamProject.fromPath( self.folderPath() )
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
            fileInfo = RamFileManager.decomposeRamsesFileName( f )
            if fileInfo['step'] != "":
                step = project.step( fileInfo['step'] )
                if step is not None:
                    stepsList.append( step )

        return stepsList

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

        # If we're online, ask the client (return a dict)
        if Ramses.instance().online():
            reply = daemon.getAsset( self._shortName )
            # check if successful
            if RamDaemonInterface.checkReply( reply ):
                self._group = reply['content']['group']
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