import os, re, shutil
from datetime import datetime

from .ramses import Ramses
from .ram_settings import RamSettings
from .utils import intToStr
from .logger import log
from .constants import LogLevel, ItemType, Log, FolderNames

# Keep the settings at hand
settings = RamSettings.instance()

class RamFileManager():
    """A Class to help managing files using the Ramses naming scheme"""

    @staticmethod
    def getFileWithResource( folder, resource):
        """returns the list of filepath corresponding to the given resource string contained in the folder"""
        if not os.path.isdir( folder ):
            return ()

        files = []

        for file in os.listdir( folder ):
            fileInfo = RamFileManager.decomposeRamsesFileName( file )
            if fileInfo['resource'] == resource:
                files.append( RamFileManager.buildPath((
                    folder,
                    file
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
                        stepInfo = RamFileManager.decomposeRamsesFileName( stepFolder )
                        if stepInfo is not None:
                            if stepInfo['step'] == stepShortName:
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
                    shotInfo = RamFileManager.decomposeRamsesFileName( shotFolder )
                    if shotInfo is not None:
                        if shotInfo['step'] == shotShortName:
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

        fileInfo = RamFileManager.decomposeRamsesFilePath( path )
        if fileInfo is None:
            return ""

        if os.path.isfile( path ):
            saveFolder = os.path.dirname( path )
        else:
            saveFolder = path

        if RamFileManager.inReservedFolder( path ):
            saveFolder = os.path.dirname( saveFolder )

        # Check if this is a restored file
        resourceStr = re.sub( '\+restored-v\d+\+', "", fileInfo['resource'])

        saveFileName = RamFileManager.buildRamsesFileName(
            fileInfo['project'],
            fileInfo['step'],
            fileInfo['extension'],
            fileInfo['type'],
            fileInfo['object'],
            resourceStr,
            )

        return saveFolder + '/' + saveFileName
        
    @staticmethod
    def restoreVersionFile( filePath ):
        if not RamFileManager.inVersionsFolder( filePath ):
            log( "This version can't be restored, it is not in a Ramses versions subfolder.", LogLevel.Critical )
            return

        fileName = os.path.basename( filePath )
        decomposedVersionFile = RamFileManager.decomposeRamsesFileName( fileName )
        if decomposedVersionFile is None:
            log( Log.MalformedName, LogLevel.Critical )
            return

        restoredFileName = RamFileManager.buildRamsesFileName(
            decomposedVersionFile['project'],
            decomposedVersionFile['step'],
            decomposedVersionFile['extension'],
            decomposedVersionFile['type'],
            decomposedVersionFile['object'],
            decomposedVersionFile['resource'] + "+restored-v" + str(decomposedVersionFile['version']) + "+",
        )

        versionFolder = os.path.dirname( filePath )
        saveFolder = os.path.dirname( versionFolder )

        restoredFilePath = saveFolder + '/' + restoredFileName
        shutil.copy2( filePath, restoredFilePath )
        return restoredFilePath

    @staticmethod
    def copyToPublish( filePath ):
        """Copies the given file to its corresponding publish folder"""

        if not os.path.isfile( filePath ):
            raise Exception( "Missing File: Cannot publish a file which does not exists: " + filePath )

        log("Publishing file: " + filePath, LogLevel.Debug)

        # Check File Name
        fileName = os.path.basename( filePath )
        decomposedFileName = RamFileManager.decomposeRamsesFileName( fileName )
        if not decomposedFileName:
            log( Log.MalformedName, LogLevel.Critical )
            return

        newFileName = RamFileManager.buildRamsesFileName(
            decomposedFileName['project'],
            decomposedFileName['step'],
            decomposedFileName['extension'],
            decomposedFileName['type'],
            decomposedFileName['object'],
            decomposedFileName['resource']
        )

        publishFolder = RamFileManager.getPublishFolder( filePath )

        newFilePath = RamFileManager.buildPath ((
            publishFolder,
            newFileName
        ))
        shutil.copy2( filePath, newFilePath )
        return newFilePath

    @staticmethod
    def copyToVersion( filePath, increment = False, stateShortName="" ):
        """Copies and increments a file into the version folder
        
        Returns the filePath of the new file version"""

        if not os.path.isfile( filePath ):
            raise Exception( "Missing File: Cannot increment a file which does not exists: " + filePath )
      
        log("Incrementing version for file: " + filePath, LogLevel.Debug)

        # Check File Name
        fileName = os.path.basename( filePath )
        decomposedFileName = RamFileManager.decomposeRamsesFileName( fileName )
        if not decomposedFileName:
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

        newFileName = RamFileManager.buildRamsesFileName(
            decomposedFileName['project'],
            decomposedFileName['step'],
            decomposedFileName['extension'],
            decomposedFileName['type'],
            decomposedFileName['object'],
            decomposedFileName['resource'],
            versionNumber,
            versionState,
        )

        versionsFolder = RamFileManager.getVersionFolder( filePath )

        newFilePath = versionsFolder + '/' + newFileName
        shutil.copy2( filePath, newFilePath )
        return newFilePath

    @staticmethod
    def getLatestVersion( filePath, defaultStateShortName="v", previous = False ):
        """Gets the latest version number and state of a file
        
        Returns a tuple (version, state)
        """

        latestVersionFilePath = RamFileManager.getLatestVersionFilePath( filePath, previous )
        if latestVersionFilePath == "":
            return ( 0, defaultStateShortName, datetime.now() )

        version = 0
        state = defaultStateShortName

        latestVersionFile = os.path.basename( latestVersionFilePath )
        decomposedVersionFile = RamFileManager.decomposeRamsesFileName(latestVersionFile)
        if decomposedVersionFile is None:
            return ( 0, defaultStateShortName, datetime.now() )

        version = decomposedVersionFile['version']
        state = decomposedVersionFile["state"]
        date = datetime.fromtimestamp(
            os.path.getmtime( latestVersionFilePath )
        )

        return (version, state, date)

    @staticmethod
    def getLatestVersionFilePath( filePath, previous=False ):
        # Check File Name
        fileName = os.path.basename( filePath )
        decomposedFileName = RamFileManager.decomposeRamsesFileName( fileName )
        if not decomposedFileName:
            log( Log.MalformedName, LogLevel.Critical )

        # Get versions
        versionsFolder = RamFileManager.getVersionFolder( filePath )

        foundFiles = os.listdir( versionsFolder )
        highestVersion = 0

        versionFilePath = ''
        prevVersionFilePath = ''
        
        for foundFile in foundFiles:
            if not os.path.isfile( versionsFolder + '/' + foundFile ): # This is in case the user has created folders in _versions
                continue

            decomposedFoundFile = RamFileManager.decomposeRamsesFileName(foundFile)

            if decomposedFoundFile == None:
                continue
            if decomposedFoundFile['project'] != decomposedFileName['project']:
                continue
            if decomposedFoundFile['type'] != decomposedFileName['type']:
                continue
            if decomposedFoundFile['object'] != decomposedFileName['object']:
                continue
            if decomposedFoundFile['step'] != decomposedFileName['step']:
                continue
            if decomposedFoundFile['resource'] != decomposedFileName['resource']:
                continue
            if decomposedFoundFile["version"] == -1:
                continue

            version = decomposedFoundFile["version"]
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
        decomposedFileName = RamFileManager.decomposeRamsesFileName( fileName )
        if not decomposedFileName:
            log( Log.MalformedName, LogLevel.Critical )

        # Get versions
        versionsFolder = RamFileManager.getVersionFolder( filePath )

        foundFiles = os.listdir( versionsFolder )
        versionFiles = []

        for foundFile in foundFiles:
            foundFilePath = versionsFolder + '/' + foundFile
            if not os.path.isfile( foundFilePath ): # This is in case the user has created folders in _versions
                continue
            
            decomposedFoundFile = RamFileManager.decomposeRamsesFileName(foundFile)
            if decomposedFoundFile == None:
                continue
            if decomposedFoundFile['project'] != decomposedFileName['project']:
                continue
            if decomposedFoundFile['type'] != decomposedFileName['type']:
                continue
            if decomposedFoundFile['object'] != decomposedFileName['object']:
                continue
            if decomposedFoundFile['step'] != decomposedFileName['step']:
                continue
            if decomposedFoundFile['resource'] != decomposedFileName['resource']:
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
    def composeRamsesFileName( ramsesFileNameDict, increment=False ):
        """Builds a filename from a dict as returned by RamFileManager.decomposeRamsesFileName().
        
        The dict must contain:
            - 'project' optional
            - 'type'
            - 'object' optional
            - 'step' 
            - 'resource' optional
            - "state" optional
            - "version" int optional
            - "extension" optional
        If "extension" does not start with a '.' it will be prepended.

        If increment is true, increments the version by 1
        """

        version = ramsesFileNameDict['version']
        if increment:
            if version <= 0:
                version = 1
            else:
                version = version + 1

        return RamFileManager.buildRamsesFileName(
            ramsesFileNameDict['project'],
            ramsesFileNameDict['step'],
            ramsesFileNameDict['extension'],
            ramsesFileNameDict['type'],
            ramsesFileNameDict['object'],
            ramsesFileNameDict['resource'],
            version,
            ramsesFileNameDict['state']
        )

    @staticmethod
    def buildRamsesFileName( project , step='' , ext="" , ramType = ItemType.GENERAL , object = '' , resource = "" , version = -1 , version_prefix = 'v' ):
        """Used to build a filename respecting Ramses' naming conventions.

        The name will look like this:
            projShortName_ramType_objectShortName_stepShortName_resourceStr_versionBlock.extension
        Ramses names follow these rules:
        - ramType can be one of the following letters: A (asset), S (shot), G (general).
        - there is an objectShortName only for assets and shots.
        - resourceStr is optional. It only serves to differentiate the main working file and its resources, that serve as secondary working files.
        - versionBlock is optional. It's made of an optional version prefix ('wip', 'v', 'pub', ...) followed by a version number.
            Version prefixes consist of all the available states' shortnames ( see Ramses.getStates() ) and some additional prefixes ( see Ramses._versionPrefixes ).
        For more information on Ramses' naming conventions (such as length limitation, allowed characters...), refer to the documentation.

        If "ext" does not start with a '.' it will be prepended.

        Args:
            project: str
            step: str
            ext: str
                The Extension. If it does not start with a '.', it will be prepended.
            ramType: str
                One of the following: 'A' (asset), 'S' (shot), 'G' (general)
            objectShortName: str
            resourceStr: str
                Serves to differentiate the main working file and its resources, that serve as secondary working files.
            version: int
            version_prefix: str

        Returns: str
        """

        resource = RamFileManager._fixResourceStr( resource )

        ramsesFileBlocks = (project)

        if ramType != '':
            ramsesFileBlocks.append( ramType )

        if ramType in (ItemType.ASSET, ItemType.SHOT) and object != "":
            ramsesFileBlocks.append( object )

        if step != "":
            ramsesFileBlocks.append( step )

        if ramType == ItemType.GENERAL and object != "":
            ramsesFileBlocks.append( object )

        if resource != '':
            ramsesFileBlocks.append( resource )

        if version != -1:
            v = version_prefix + intToStr(version)
            ramsesFileBlocks.append( v )

        ramsesFileName = '_'.join( ramsesFileBlocks )
        
        if ext != '':
            if not ext.startswith('.'):
                ext = '.' + ext
            ramsesFileName = ramsesFileName + ext

        return ramsesFileName

    @staticmethod
    def decomposeRamsesFilePath( path ):
        """Tries to get the maximum information from the path,
        returns a dict similar to decomposeRamsesFileName"""

        blocks = {
            "project": "",
            "type": "",
            "object": "",
            "step": "",
            "resource": "",
            "state": "",
            "version": -1,
            "extension": "",
        }

        name = os.path.basename( path )

        # First get information specific to files or innest folder, won't be found in parent folders:
        decomposedName = RamFileManager.decomposeRamsesFileName( name )
        print(decomposedName)
        if decomposedName is not None:
            blocks = decomposedName

        # Move up to the parent folder
        path = os.path.dirname(path)
        name = os.path.basename(path)

        # Move up the tree until we've found something which can be decomposed
        while name != '':
            # If we've found all the info, we can return
            if blocks['project'] != '' and blocks['type'] != '' and blocks['object'] != '' and blocks['step'] != '':
                return blocks

            # Try to get more info from the folder name
            decomposedName = RamFileManager.decomposeRamsesFileName( name )
            if decomposedName is not None:
                if blocks['project'] == '':
                    blocks['project'] = decomposedName['project']
                if blocks['type'] == '':
                    blocks['type'] = decomposedName['type']
                if blocks['object'] == '':
                    blocks['object'] = decomposedName['object']
                if blocks['step'] == '':
                    blocks['step'] = decomposedName['step']

            # We got to the project folder, no need to continue
            if RamFileManager.isProjectFolder( path ):
                # The project short name can still be found from the project folder
                if blocks['project'] == '':
                    blocks['project'] = name
                return blocks

            # Move up to the parent folder
            path = os.path.dirname(path)
            name = os.path.basename(path)
        
        return blocks

    @staticmethod
    def decomposeRamsesFileName( ramsesFileName ):
        """Used on files that respect Ramses' naming convention: it separates the name into blocks (one block for the project's shortname, one for the step, one for the extension...)

        A Ramses filename can have all of these blocks:
        - projectID_ramType_objectShortName_ramStep_resourceStr_versionBlock.extension
        - ramType can be one of the following letters: A (asset), S (shot), G (general).
        - there is an objectShortName only for assets and shots.
        - resourceStr is optional. It only serves to differentiate the main working file and its resources, that serve as secondary working files.
        - versionBlock is optional. It's made of two blocks: an optional version prefix, also named state, followed by a version number.
            Version prefixes consist of all the available states' shortnames ( see Ramses.getStates() ) and some additional prefixes ( see Ramses._versionPrefixes ). Eg. 'wip', 'v', ...
        For more information on Ramses' naming conventions (such as length limitation, forbidden characters...), refer to the documentation.

        Arg:
            ramsesFileName: str
        
        Returns: dict or None
            If the file does not match Ramses' naming convention, returns None.
            Else, returns a dictionary made of all the blocks: {"projectId", 'type', 'object', 'step', 'resource', "state", "version", "extension"}
        """
        if type(ramsesFileName) != str:
            raise TypeError( "ramsesFileName must be a string." )

        splitRamsesName = re.match(RamFileManager._getRamsesNameRegEx(), ramsesFileName)

        if splitRamsesName == None:
            return None

        project = splitRamsesName.group(1)
        ramType = splitRamsesName.group(2)
        objectShortName = ''
        step = ''
        resource = ''
        state = ''
        version = -1
        extension = ''

        if ramType in (ItemType.ASSET, ItemType.SHOT):
            objectShortName = splitRamsesName.group(3)
            if splitRamsesName.group(4) is not None:
                step = splitRamsesName.group(4)
        else:
            step = splitRamsesName.group(3)
            if splitRamsesName.group(4) is not None:
                objectShortName = splitRamsesName.group(4)

        if splitRamsesName.group(5) is not None:
            resource = splitRamsesName.group(5)
        
        if splitRamsesName.group(6) is not None:
            state = splitRamsesName.group(6)

        if splitRamsesName.group(7) is not None:
            version = int ( splitRamsesName.group(7) )

        if splitRamsesName.group(8) is not None:
            extension = splitRamsesName.group(8)

        blocks = {
            'project': project,
            'type': ramType,
            'object': objectShortName,
            'step': step,
            'resource': resource,
            'state': state,
            'version': version,
            'extension': extension,
        }

        return blocks

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
        if re.match( '^([a-z0-9+-]{1,10})_([ASG])_([a-z0-9+-]{1,10})', n , re.IGNORECASE): return True
        return False

    @staticmethod
    def _getRamsesNameRegEx():
        """Low-level, undocumented. Used to get a Regex to check if a file matches Ramses' naming convention.
        """
        regexStr = RamFileManager._getVersionRegExStr()

        regexStr = '^([a-z0-9+-]{1,10})_(?:([ASG])_([a-z0-9+-]{1,10}))(?:_([a-z0-9+-]{1,10}))?(?:_((?!(?:' + regexStr + ')?[0-9]+)[a-z0-9+\\s-]+))?(?:_(' + regexStr + ')?([0-9]+))?(?:\\.([a-z0-9.]+))?$'

        regex = re.compile(regexStr, re.IGNORECASE)
        return regex

    @staticmethod
    def _getVersionRegExStr():
        """Low-level, undocumented. Used to get a Regex str that can be used to identify version blocks.

        A version block is composed of an optional version prefix and a version number.
        'wip002', 'v10', '1002' are version blocks; '002wip', '10v', 'v-10' are not.\n
        Version prefixes consist of all the available states' shortnames ( see Ramses.getStates() ) and some additional prefixes ( see Ramses._versionPrefixes ).
        """
        
        prefixes = settings.versionPrefixes

        for state in Ramses.instance().states():
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
        d = RamFileManager.decomposeRamsesFileName(fileName)
        return d['version']