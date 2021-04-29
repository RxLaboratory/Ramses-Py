import os

from .ramses import Ramses
from .ramObject import RamObject
from .ramStatus import RamStatus
from .ramStep import RamStep


class RamItem( RamObject ):
    """
    Base class for RamAsset and RamShot.
    An item of the project, either an asset or a shot.
    """

    def __init__( self, itemName, itemShortName, itemFolder="" ):
        """
        Args:
            itemName (str)
            itemShortName (str)
            itemFolder (str, optional): Defaults to "".
        """
        super().__init__( itemName, itemShortName )
        self._folderPath = itemFolder

    def currentStatus( self, step, resource="" ): #TODO if online
        """The current status for the given step

        Args:
            step (RamStep or str): The step.
            resource (str, optional): The name of the resource. Defaults to "".

        Returns:
            RamStatus
        """
        if not Ramses.instance:
            raise Exception( "Ramses has to be instantiated first." )
        # If we're online, ask the client
        if Ramses.instance.online:
            # TODO ask the client
            return None
        
        # If offline
        currentVersionPath = self.versionFilePath( step, resource )
        if currentVersionPath == None:
            print( "There was an error getting the latest version or none was found." )
            return None

        currentVersionPath = self._folderPath + '/' + currentVersionPath
        currentVersionPath = Ramses.instance.currentProject().absolutePath( currentVersionPath )

        currentStatus = RamStatus.getFromPath( currentVersionPath )

        return currentStatus

    # Do not document "type" and "assetGroup" arguments, they should stay hidden
    # (not needed in derived classes RamShot.folderPath() and RamAsset.folderPath())
    def folderPath( self, itemType, step="", assetGroup="" ): #TODO
        """The absolute path to the folder containing the asset, or to the step subfolder if provided

        Args:
            step (RamStep or str, optional): Defaults to "".

        Returns:
            str
        """

        # NOTE :
        # if self._folderPath is not "": return self._folderPath
        # sinon:
            # if itemType == 'SHOT' -> construire chemin d'un shot
            # if itemType == 'ASSET -> construire le chemin en prenant en compte assetgroup
            # self._folderPath = résultat de ci dessus (pour pas avoir à reconstruire à chaque fois)
            # return self._folderPath

        pass

    def latestVersion( self, step, resource="", stateId="wip"): #TODO if online
        """Returns the highest version number for the given state (wip, pub…).

        Args:
            step (RamStep or str)
            resource (str, optional): Defaults to "".
            stateId (str, optional): Defaults to "wip".

        Returns:
            int
        """
        if not Ramses.instance:
            raise Exception( "Ramses has to be instantiated first." )
 
        # If we're online, ask the client
        if Ramses.instance.online:
            # TODO
            return 0

        # Else check in the folders
        if self.folderPath == '':
            print( "The given item has no folderPath." )
            return None

        folderPath = Ramses.instance.currentProject().folderPath + '/' + self.folderPath #Makes it absolute

        if not os.path.isdir( folderPath ):
            print( "The given item's folder was not found.\nThis is the path that was checked:\n" + folderPath )
            return None
        if not isinstance( stateId, str ):
            raise TypeError( "State must be a str" )

        stepShortName = ""
        if isinstance( step, str ):
            stepShortName = step
        elif isinstance( step, RamStep ):
            stepShortName = step.shortName
        else:
            raise TypeError( "Step must be a str or an instance of RamStep" )

        baseName = os.path.basename( self._folderPath ) + '_' + stepShortName #Name without the resource str (added later)
        stepFolderPath = folderPath + '/' + baseName

        if os.path.isdir( stepFolderPath ) == False:
            print( "The folder for the following step: " + stepShortName + " has not been found." )
            return None
        if os.path.isdir( stepFolderPath + '/ramses_versions' ) == False:
            print( "ramses_versions directory has not been found" )
            return None

        foundFiles = os.listdir( stepFolderPath + '/ramses_versions' )
        highestVersion = 0

        for foundFile in foundFiles:
            if not os.path.isfile( stepFolderPath + '/ramses_versions/' + foundFile ): #This is in case the user has created folders in ramses_versions
                continue

            decomposedFoundFile = Ramses.instance._decomposeRamsesFileName( foundFile )

            if decomposedFoundFile == None:
                continue
            if not foundFile.startswith( baseName ): #In case other assets have been misplaced here
                continue
            if decomposedFoundFile["resourceStr"] != resource:
                continue
            if decomposedFoundFile["version"] == '':
                continue
            if decomposedFoundFile["state"] != stateId:
                continue
            
            versionInt = int( decomposedFoundFile["version"] )
            if versionInt > highestVersion:
                highestVersion = versionInt

        return highestVersion

    def previewFolderPath( self, step ): #TODO
        """Gets the path to the preview folder.
            Paths are relative to the root of the item folder.

        Args:
            step (RamStep or str)

        Returns:
            str
        """
        pass

    def previewFilePaths( self, step, resource="" ): #TODO
        """Gets the list of file paths in the preview folder.
            Paths are relative to the root of the item folder.

        Args:
            step (RamStep or str)
            resource (str, optional): Defaults to "".

        Returns:
            list of str
        """
        pass

    def publishedFolderPath( self, step ): #TODO
        """Gets the path to the publish folder.
        Paths are relative to the root of the item folder.

        Args:
            step (RamStep or str)   

        Returns:
            str
        """
        pass

    def publishedFilePaths( self, step, resource="" ):
        """Gets the list of file paths in the publish folder.
            Paths are relative to the root of the item folder.

        Args:
            step (RamStep or str)
            resource (str, optional): Defaults to "".

        Returns:
            list of str
        """
        if not Ramses.instance:
            raise Exception( "Ramses has to be instantiated first." )

        if isinstance( step, str ):
            stepShortName = step
        elif isinstance( step, RamStep ):
            stepShortName = step.shortName
        else:
            raise TypeError( "Step must be a str or an instance of RamStep" )

        if self.folderPath == '':
            print( "The given item has no folderPath." )
            return None

        baseName = os.path.basename( self._folderPath )
        folderPath = Ramses.instance.currentProject().folderPath + '/' + self.folderPath

        if not os.path.isdir( folderPath ):
            print( "The given item's folder was not found.\nThis is the path that was checked:\n" + folderPath )
            return None
        
        folderPath = folderPath + '/' + baseName + '_' + stepShortName
        if not os.path.isdir( folderPath + '/ramses_publish' ):
            print( "ramses_publish directory has not been found" )
            return None

        foundFiles = os.listdir( folderPath + '/ramses_publish' )
        foundFilePath = ""
        publishFiles = []

        for foundFile in foundFiles:
            if os.path.isdir( foundFile ):
                continue

            blocks = Ramses.instance._decomposeRamsesFileName( foundFile )

            if blocks == None:
                continue
            if blocks[ "resourceStr" ] != resource:
                continue
            if not foundFile.startswith( baseName ):
                continue

            #Building file path relative to root of item folder
            foundFilePath = baseName + '_' + stepShortName + '/ramses_publish/' + foundFile
            publishFiles.append(foundFilePath)
            
        return publishFiles

    def versionFolderPath( self, step ): #TODO
        """Path to the version folder relative to the item root folder

        Args:
            step (RamStep)

        Returns:
            str
        """
        pass

    def versionFilePath( self, step, resource="" ): #TODO if online
        """Latest version file path relative to the item root folder

        Args:
            step (RamStep)
            resource (str, optional): Defaults to "".

        Returns:
            str
        """ 
        if not Ramses.instance:
            raise Exception( "Ramses has to be instantiated first." )

        # If we're online, ask the client
        if Ramses.instance.online:
            #TODO ask the client
            return None
        
        # Else check in the folders
        # It is basically the same as getLatestVersion. Only difference is that it does not take the stateId into account
        # and returns the path instead of the version number.
        if self.folderPath == '':
            print( "The given item has no folderPath." )
            return None

        folderPath = Ramses.instance.currentProject().absolutePath( self.folderPath )

        if not os.path.isdir( folderPath ):
            print( "The given item's folder was not found.\nThis is the path that was checked:\n" + folderPath )
            return None

        if isinstance( step, str ):
            stepShortName = step
        elif isinstance( step, RamStep ):
            stepShortName = step.shortName
        else:
            raise TypeError( "Step must be a str or an instance of RamStep" )

        baseName = os.path.basename( self._folderPath ) + '_' + stepShortName # Name without the resource str (added later)
        stepFolderPath = folderPath + '/' + baseName

        if os.path.isdir( stepFolderPath ) == False:
            print( "The folder for the following step: " + stepShortName + " has not been found." )
            return None
        if os.path.isdir( stepFolderPath + '/ramses_versions' ) == False:
            print( "ramses_versions directory has not been found" )
            return None

        foundFiles = os.listdir( stepFolderPath + '/ramses_versions' )
        highestVersion = 0
        highestVersionFileName = ""

        for foundFile in foundFiles:
            if not os.path.isfile( stepFolderPath + '/ramses_versions/' + foundFile ): # This is in case the user has created folders in ramses_versions
                continue

            decomposedFoundFile = Ramses.instance._decomposeRamsesFileName( foundFile )

            if decomposedFoundFile == None:
                continue
            if not foundFile.startswith( baseName ): # In case other assets have been misplaced here
                continue
            if decomposedFoundFile[ "resourceStr" ] != resource:
                continue
            if decomposedFoundFile[ "version" ] == '':
                continue
            
            versionInt = int( decomposedFoundFile["version"] )
            if versionInt > highestVersion:
                highestVersion = versionInt
                highestVersionFileName = foundFile

        if highestVersionFileName == '':
            print( "No version was found" )
            return None

        highestVersionFilePath = baseName + "/ramses_versions/" + highestVersionFileName

        return highestVersionFilePath

    def wipFolderPath( self, step ): #TODO
        """Path to the WIP folder relative to the item root folder

        Args:
            step (RamStep or str)

        Returns:
            str
        """
        pass

    def wipFilePath( self, step, resource="" ): 
        """Current wip file path relative to the item root folder

        Args:
            step (RamStep or str)
            resource (str, optional): Defaults to "".

        Returns:
            str
        """
        if self.folderPath == '':
            print( "The given item has no folderPath." )
            return None

        if not isinstance(step, RamStep):
            raise TypeError( "Step must be an instance of RamStep" )

        baseName = os.path.basename( self._folderPath ) + '_' + step._shortName

        if step.fileType == None:
            raise Exception( "The given step has no fileType; cannot build the path towards the working file (missing extension)." )

        filePath = baseName + '/' + baseName + '.' + step.fileType.extension

        return filePath

    def isPublished( self, step, resource="" ):
        """Convenience function to check if there are published files in the publish folder.
            Equivalent to len(self.publishedFilePaths(step, resource)) > 0

        Args:
            step (RamStep)
            resource (str, optional): Defaults to "".

        Returns:
            bool
        """
        result = self.publishedFilePaths( step, resource )
        if result == None:
            return False
        return len( result ) > 0

    def setStatus( self, status, step ): #TODO
        """Sets the current status for the given step

        Args:
            status (RamStatus)
            step (RamStep)
        """ 
        pass

    def status( self, step ): #TODO
        """Gets the current status for the given step

        Args:
            step (RamStep)

        Returns:
            RamStatus
        """ 
        pass
