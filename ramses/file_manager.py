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

import os, re, shutil
from datetime import datetime
from threading import Thread
from .ram_settings import RamSettings
from .utils import intToStr
from .logger import log
from .constants import LogLevel, ItemType, Log, FolderNames
from .name_manager import RamNameManager

# Keep the settings at hand
settings = RamSettings.instance()

class RamFileManager():
    """A Class to help managing files using the Ramses naming scheme"""

    # Cache stuff
    __nameRe = None

    @staticmethod
    def copy( originPath, destinationPath, separateThread=True ):
        """Copies a file, in a separated thread if separateThread is True"""

        if separateThread:
            t = Thread( target=RamFileManager.copy, args=(originPath, destinationPath, False) )
            log( "Launching parallel copy of a file.", LogLevel.Debug )
            t.start()
        else:
            log("Starting copy of\n" + originPath + "\nto: " + destinationPath, LogLevel.Debug )
            shutil.copy2( originPath, destinationPath )
            log("Finished copying\n" + originPath + "\nto: " + destinationPath, LogLevel.Debug )

    @staticmethod
    def getRamsesFiles( folderPath, resource = None ):
        """Gets all files respecting the Ramses naming scheme in the given folder
        Returns a list of file paths"""
        if not os.path.isdir(folderPath):
            return []

        files = []

        for f in os.listdir(folderPath):
            nm = RamNameManager
            if nm.setFileName(f):
                if resource is None or nm.resource == resource:
                    files.append( RamFileManager.buildPath((
                        folderPath,
                        f
                    )))

        return files

    @staticmethod
    def isAssetStep( stepShortName, assetsPath ):
        """Checks the production type of the given step in the assets folder"""
        # Try to find the type from shots or assets folders
        if os.path.isdir( assetsPath ):
            # each folder is an asset group
            for folder in os.listdir( assetsPath ):
                groupPath = assetsPath + "/" + folder 
                # Check only dirs
                if not os.path.isdir( groupPath ):
                    continue
                # each folder is an asset
                for assetFolder in os.listdir( groupPath ):
                    assetPath = groupPath + '/' + assetFolder
                    if not os.path.isdir( assetPath ):
                        continue
                    # each folder is a step working folder in the asset
                    for stepFolder in os.listdir( assetPath ):
                        nm = RamNameManager()
                        if nm.setFileName( stepFolder ):
                            if nm.step == stepShortName:
                                return True
        return False

    @staticmethod
    def isShotStep( shotShortName, shotsPath ):
        """Checks the production type of the given step in the shots folder"""
        if os.path.isdir( shotsPath ):
            #  each folder is a shot
            for shotFolder in os.listdir( shotsPath ):
                shotPath = shotsPath + '/' + shotFolder
                if not os.path.isdir( shotPath ):
                    continue
                # each folder is a step working folder in the shot
                for shotFolder in os.listdir( shotPath ):
                    nm = RamNameManager()
                    if nm.setFileName( shotFolder ):
                        if nm.step == shotShortName:
                            return True
        return False

    @staticmethod
    def getProjectFolder( path ):
        """Tries to get the root folder of the project"""

        name = os.path.basename( path )

        while name != '':
            if RamFileManager.isProjectFolder( path ):
                return path
            # Move up to the parent folder
            path = os.path.dirname(path)
            name = os.path.basename(path)
        
        return ''

    @staticmethod
    def isProjectFolder( folderPath ):
        """Checks if the given folder is the project root"""
        if not os.path.isdir( folderPath ):
            return False

        foundFiles = os.listdir( folderPath )
        for foundFile in foundFiles:
            if os.path.isfile(foundFile):
                continue
            folderName = os.path.basename( foundFile )
            if folderName in (
                    '00-ADMIN',
                    '01-PRE-PROD',
                    '02-PROD',
                    '03-POST-PROD',
                    '04-ASSETS',
                    '05-SHOTS',
                    '06-EXPORT'
                ):
                return True

        return False

    @staticmethod
    def getSaveFilePath( path ):
        """Gets the save path for an existing file.
        This path is not the same as the file path if the file path is located in the versions/preview/publish subfolder"""

        nm = RamNameManager()
        nm.setFilePath( path )
        if nm.project == '':
            return ""

        if nm.ramType == '':
            return ""

        if os.path.isfile( path ):
            saveFolder = os.path.dirname( path )
        else:
            saveFolder = path

        if saveFolder == "":
            return ""

        if RamFileManager.inReservedFolder( path ):
            saveFolder = os.path.dirname( saveFolder )
            # We may still be in a reserved folder if this was published
            if RamFileManager.inReservedFolder( saveFolder ): saveFolder = os.path.dirname( saveFolder )
            # Still the case? something is wrong
            if RamFileManager.inReservedFolder( saveFolder ): return ""

        saveFileName = nm.fileName()
        
        return saveFolder + '/' + saveFileName
        
    @staticmethod
    def restoreVersionFile( filePath ):
        if not RamFileManager.inVersionsFolder( filePath ):
            log( "This version can't be restored, it is not in a Ramses version subfolder.", LogLevel.Critical )
            return

        fileName = os.path.basename( filePath )

        nm = RamNameManager()
        if not nm.setFileName( fileName ):
            log( Log.MalformedName, LogLevel.Critical )
            return

        # Set the resource, remove state and version
        nm.resource = nm.resource +  "+restored-v" + str(nm.version) + "+"
        nm.state = ""
        nm.version = -1
        restoredFileName = nm.fileName()

        versionFolder = os.path.dirname( filePath )
        saveFolder = os.path.dirname( versionFolder )

        restoredFilePath = saveFolder + '/' + restoredFileName
        RamFileManager.copy( filePath, restoredFilePath )
        return restoredFilePath

    @staticmethod
    def getPublishPath( filePath ):
        """Copies the given file to its corresponding publish folder"""
        from .metadata_manager import RamMetaDataManager

        newFilePath = RamFileManager.getPublishPath( filePath )
        if newFilePath == "":
            return
        RamFileManager.copy( filePath, newFilePath )
        RamMetaDataManager.appendHistoryDate( newFilePath )
        return newFilePath

    @staticmethod
    def getPublishPath( filePath ):
        """Gets the publish path of the given file (including the version subfolder)"""
        from .metadata_manager import RamMetaDataManager

        if not os.path.isfile( filePath ):
            raise Exception( "Missing File: Cannot publish a file which does not exists: " + filePath )

        log("Getting pulbish file: " + filePath, LogLevel.Debug)

        # Check File Name
        fileName = os.path.basename( filePath )
        nm = RamNameManager()
        if not nm.setFileName( fileName ):
            log( Log.MalformedName, LogLevel.Critical )
            return ""

        newFileName = nm.fileName()

        publishFolder = RamFileManager.getPublishFolder( filePath )

        # Check version
        versionTuple = RamFileManager.getLatestVersion( filePath )
        # Subfolder name
        versionFolder = intToStr( versionTuple[0] )
        if (versionTuple[0] == 0): versionFolder = intToStr( 1 )
        if versionTuple[1] != "" and versionTuple[1] != "v":
            versionFolder = versionFolder + "_" + versionTuple[1]

        newFilePath = RamFileManager.buildPath ((
            publishFolder,
            versionFolder
        ))

        if not os.path.isdir( newFilePath ):
            os.makedirs( newFilePath )

        newFilePath = RamFileManager.buildPath ((
            newFilePath,
            newFileName
        ))

        # Keep the date in the metadata, just in case
        RamMetaDataManager.setDate( filePath, versionTuple[2] )
        
        return newFilePath

    @staticmethod
    def copyToVersion( filePath, increment = False, stateShortName="" ):
        """Copies and increments a file into the version folder
        
        Returns the filePath of the new file version"""
        from .metadata_manager import RamMetaDataManager

        if not os.path.isfile( filePath ):
            raise Exception( "Missing File: Cannot increment a file which does not exists: " + filePath )
      
        log("Incrementing version for file: " + filePath, LogLevel.Debug)

        # Check File Name
        fileName = os.path.basename( filePath )
        nm = RamNameManager()
        if not nm.setFileName( fileName ):
            log( Log.MalformedName, LogLevel.Critical )
            return
               
        # Look for the latest version to increment and save
        version = RamFileManager.getLatestVersion( filePath, stateShortName )
        versionNumber = version[0]
        if stateShortName == "":
            versionState = version[1]
        else:
            versionState = stateShortName

        if increment:
            versionNumber = versionNumber + 1

        if versionNumber <= 0:
            versionNumber = 1

        nm.version = versionNumber
        nm.state = versionState
        newFileName = nm.fileName()

        versionsFolder = RamFileManager.getVersionFolder( filePath )

        newFilePath = versionsFolder + '/' + newFileName
        RamFileManager.copy( filePath, newFilePath )
        RamMetaDataManager.appendHistoryDate( newFilePath )
        return newFilePath

    @staticmethod
    def getLatestVersion( filePath, defaultStateShortName="v", previous = False ):
        """Gets the latest version number and state of a file
        
        Returns a tuple (version, state, date)
        """

        latestVersionFilePath = RamFileManager.getLatestVersionFilePath( filePath, previous )
        if latestVersionFilePath == "":
            return ( 0, defaultStateShortName, datetime.now() )

        version = 0
        state = defaultStateShortName

        latestVersionFile = os.path.basename( latestVersionFilePath )
        nm = RamNameManager()
        if not nm.setFileName( latestVersionFile ):
            return ( 0, defaultStateShortName, datetime.now() )

        version = nm.version
        state = nm.state
        date = datetime.fromtimestamp(
            os.path.getmtime( latestVersionFilePath )
        )

        return (version, state, date)

    @staticmethod
    def getLatestVersionFilePath( filePath, previous=False ):
        # Check File Name
        fileName = os.path.basename( filePath )
        nm = RamNameManager()
        if not nm.setFileName( fileName ):
            log( Log.MalformedName, LogLevel.Critical )
            return ''

        # Get versions
        versionsFolder = RamFileManager.getVersionFolder( filePath )

        foundFiles = os.listdir( versionsFolder )
        highestVersion = 0

        versionFilePath = ''
        prevVersionFilePath = ''
        
        for foundFile in foundFiles:
            if not os.path.isfile( versionsFolder + '/' + foundFile ): # This is in case the user has created folders in _versions
                continue

            foundNM = RamNameManager()
            if not foundNM.setFileName( foundFile ):
                continue
            if foundNM.project != nm.project:
                continue
            if foundNM.ramType != nm.ramType:
                continue
            if foundNM.shortName != nm.shortName:
                continue
            if foundNM.step != nm.step:
                continue
            if foundNM.resource != nm.resource:
                continue
            if foundNM.version == -1:
                continue

            version = foundNM.version
            if version > highestVersion:
                highestVersion = version
                prevVersionFilePath = versionFilePath
                versionFilePath = versionsFolder + '/' + foundFile

        if previous:
            return prevVersionFilePath

        return versionFilePath

    @staticmethod
    def getVersionFilePaths( filePath ):
        # Check File Name
        fileName = os.path.basename( filePath )
        nm = RamNameManager()
        if not nm.setFileName( fileName ):
            log( Log.MalformedName, LogLevel.Critical )

        # Get versions
        versionsFolder = RamFileManager.getVersionFolder( filePath )

        foundFiles = os.listdir( versionsFolder )
        versionFiles = []

        for foundFile in foundFiles:
            foundFilePath = versionsFolder + '/' + foundFile
            if not os.path.isfile( foundFilePath ): # This is in case the user has created folders in _versions
                continue
            
            foundNM = RamNameManager()
            if not foundNM.setFileName( foundFile ):
                continue
            if foundNM.project != nm.project:
                continue
            if foundNM.ramType != nm.ramType:
                continue
            if foundNM.shortName != nm.shortName:
                continue
            if foundNM.step != nm.step:
                continue
            if foundNM.resource != nm.resource:
                continue

            versionFiles.append( foundFilePath )

        versionFiles.sort( key = RamFileManager._versionFilesSorter )
        return versionFiles

    @staticmethod
    def getVersionFolder( filePath ):
        """Gets the versions folder for this file"""

        fileFolder = os.path.dirname( filePath )
        versionsFolderName = settings.folderNames.versions

        if RamFileManager.inVersionsFolder( filePath ):
            versionsFolder = fileFolder

        elif RamFileManager.inPublishFolder( filePath ) or RamFileManager.inPreviewFolder( filePath ):
            wipFolder = os.path.dirname( fileFolder )
            versionsFolder = wipFolder + '/' + versionsFolderName
        
        else:
            versionsFolder = fileFolder + '/' + versionsFolderName

        if not os.path.isdir( versionsFolder ):
            os.makedirs( versionsFolder )

        return versionsFolder

    @staticmethod
    def getPublishFolder( filePath ):
        """Gets the published folder for this file"""

        fileFolder = os.path.dirname( filePath )
        publishFolderName = settings.folderNames.publish

        if RamFileManager.inPublishFolder( filePath ):
            publishFolder = fileFolder

        elif RamFileManager.inVersionsFolder( filePath ) or RamFileManager.inPreviewFolder( filePath ):
            wipFolder = os.path.dirname( fileFolder )
            publishFolder = wipFolder + '/' + publishFolderName

        else:
            publishFolder = fileFolder + '/' + publishFolderName

        if not os.path.isdir( publishFolder ):
            os.makedirs( publishFolder )

        return publishFolder

    @staticmethod
    def inPreviewFolder( path ):
        """Checks if the given path is inside a "preview" folder"""
        currentFolder = os.path.dirname(path)
        currentFolderName = os.path.basename( currentFolder )
        return currentFolderName == settings.folderNames.preview

    @staticmethod
    def inPublishFolder( path ):
        """Checks if the given path is inside a "published" folder"""
        currentFolder = os.path.dirname(path)
        currentFolderName = os.path.basename( currentFolder )
        if currentFolderName == settings.folderNames.publish: return True
        currentFolder = os.path.dirname(currentFolder)
        currentFolderName = os.path.basename( currentFolder )
        return currentFolderName == settings.folderNames.publish

    @staticmethod
    def inVersionsFolder( path ):
        """Checks if the given path is inside a "versions" folder"""
        currentFolder = os.path.dirname(path)
        currentFolderName = os.path.basename( currentFolder )
        return currentFolderName == settings.folderNames.versions

    @staticmethod
    def inReservedFolder( path ):
        """Checks if the given path is (directly) inside a "versions/preview/published" folder"""
        if os.path.isfile( path ):
            currentFolder = os.path.dirname( path )
            currentFolderName = os.path.basename( currentFolder )
        else:
            currentFolderName = os.path.basename( path )

        return currentFolderName in [
            FolderNames.versions,
            FolderNames.publish,
            FolderNames.preview
        ]
    
    @staticmethod
    def validateName( name ):
        """Checks if the name is valid, respects the Ramses naming scheme"""

        # Accept empty names
        if name == "":
            return True

        regex = re.compile('^[ a-zA-Z0-9+-]{1,256}$', re.IGNORECASE)
        if re.match(regex, name):
            return True
        return False

    @staticmethod
    def validateShortName( name ):
        """Checks if the name is valid, respects the Ramses naming scheme"""
        regex = re.compile('^[a-z0-9+-]{1,10}$', re.IGNORECASE)
        if re.match(regex, name):
            return True
        return False

    @staticmethod
    def buildPath( folders ):
        """Builds a path with a list of folder names or subpaths,
        adding the '/' only if needed, and ignoring empty blocks"""

        fullPath = ''

        for folder in folders:
            if folder == '':
                continue
            if not fullPath.endswith('/') and not fullPath == '':
                fullPath = fullPath + '/'
                
            fullPath = fullPath + folder

        return fullPath

    @staticmethod
    def _isRamsesItemFoldername( n ):
        """Low-level, undocumented. Used to check if a given folder respects Ramses' naming convention for items' root folders.
        
        The root folder should look like this:
            projectID_ramType_objectShortName

        Returns: bool
        """
        if re.match( '^([a-z0-9+-]{1,10})_([ASG])_([a-z0-9+-]{1,10})$', n , re.IGNORECASE): return True
        return False

    @staticmethod
    def _getRamsesNameRegEx():
        """Low-level, undocumented. Used to get a Regex to check if a file matches Ramses' naming convention.
        """

        if RamFileManager.__nameRe is not None:
            return RamFileManager.__nameRe

        regexStr = RamFileManager._getVersionRegExStr()

        regexStr = '^([a-z0-9+-]{1,10})_(?:([ASG])_((?!(?:' + regexStr + ')[0-9]+)[a-z0-9+-]{1,10}))(?:_((?!(?:' + regexStr + ')[0-9]+)[a-z0-9+-]{1,10}))?(?:_((?!(?:' + regexStr + ')[0-9]+)[a-z0-9+\\s-]+))?(?:_(' + regexStr + ')?([0-9]+))?(?:\\.([a-z0-9.]+))?$'

        regex = re.compile(regexStr, re.IGNORECASE)

        RamFileManager.__nameRe = regex
        return regex

    @staticmethod
    def _getVersionRegEx():
        """Low-leve, undocumented. Builds a Regex to find the version and state in a given file name.
        group #0 is the underscore + versionblock + extension _v12.abc
        group #1 is the underscore + versionblock _v12
        group #2 is the state v (or empty)
        group #3 is version 12
        """

        states = RamFileManager._getVersionRegExStr()
        regexStr = '(?:(_' + states + ')?([0-9]+)))(?:\\.[a-z0-9.]+)?$'
        regex = re.compile(regexStr, re.IGNORECASE)
        return regex

    @staticmethod
    def _getVersionRegExStr():
        """Low-level, undocumented. Used to get a Regex str that can be used to identify version blocks.

        A version block is composed of an optional version prefix and a version number.
        'wip002', 'v10', '1002' are version blocks; '002wip', '10v', 'v-10' are not.\n
        Version prefixes consist of all the available states' shortnames ( see Ramses.getStates() ) and some additional prefixes ( see Ramses._versionPrefixes ).
        """

        from .ramses import Ramses
        ramses = Ramses.instance()
        
        prefixes = settings.versionPrefixes

        states = ramses.states()

        for state in states:
            prefixes.append( state.shortName() )

        return '|'.join(prefixes)
        
    @staticmethod
    def _fixResourceStr( resourceStr ):
        """Low-level, undocumented. Used to remove all forbidden characters from a resource.

        Returns: str
        """
        forbiddenCharacters = {
            '"' : ' ',
            '_' : '-',
            '[' : '-',
            ']' : '-',
            '{' : '-',
            '}' : '-',
            '(' : '-',
            ')' : '-',
            '\'': ' ',
            '`' : ' ',
            '.' : '-',
            '/' : '-',
            '\\' : '-',
            ',' : ' ' 
            }

        fixedResourceStr = ''
        for char in resourceStr:
            if char in forbiddenCharacters:
                fixedResourceStr = fixedResourceStr + forbiddenCharacters[char]
            else:
                fixedResourceStr = fixedResourceStr + char
        return fixedResourceStr

    @staticmethod
    def _versionFilesSorter( f ):
        fileName = os.path.basename(f)
        nm = RamNameManager()
        if not nm.setFileName( fileName ):
            return -1
        return nm.version