import os, json

from .file_manager import RamFileManager
from .constants import FileNames, MetaDataKeys

class RamMetaDataManager():
    """A Class to get/set metadata from files
    
    Ramses will use a single sidecar file in the folder where the file is contained;
    thus the metadata used by Ramses is set on a per-folder basis, and is not copied when a file is copied/moved:
    it does not make sens for Ramses to have the same metadata when a file is moved."""

    @staticmethod
    def getValue(filePath, key):
        """Gets the value of a specific key for the file"""
        data = RamMetaDataManager.getFileMetaData( filePath )
        if key in data:
            return data[key]
        return None

    @staticmethod
    def setValue(filePath, key, value):
        """Sets a value for a specific key for the file"""
        # file data
        fileData = RamMetaDataManager.getFileMetaData(filePath)
        # update comment
        fileData[key] = value
        # re-set file data
        RamMetaDataManager.setFileMetaData( filePath, fileData )

    @staticmethod
    def getVersionFilePath( filePath ):
        """Gets the version file for the file"""
        version = RamMetaDataManager.getValue(filePath, MetaDataKeys.VERSION_FILE)
        if version is None:
            return -1
        return version

    @staticmethod
    def setVersionFilePath( filePath, versionfilePath ):
        """Sets a version file for the file"""
        RamMetaDataManager.setValue(filePath, MetaDataKeys.VERSION_FILE, versionfilePath)

    @staticmethod
    def getVersion( filePath ):
        """Gets the version for the file"""
        version = RamMetaDataManager.getValue(filePath, MetaDataKeys.VERSION)
        if version is None:
            return -1
        return version

    @staticmethod
    def setVersion( filePath, version ):
        """Sets a version for the file"""
        RamMetaDataManager.setValue(filePath, MetaDataKeys.VERSION, version)

    @staticmethod
    def getComment( filePath ):
        """Gets the comment for the file"""
        comment = RamMetaDataManager.getValue(filePath, MetaDataKeys.COMMENT)
        if comment is None:
            return ''
        return comment

    @staticmethod
    def setComment( filePath, comment):
        """Sets a comment for the file"""
        RamMetaDataManager.setValue(filePath, MetaDataKeys.COMMENT, comment)

    @staticmethod
    def getMetaDataFile( path ):
        """Gets the metadata .json file for the given path"""
        folder = path
        if os.path.isfile(folder):
            folder = os.path.dirname(folder)
        if not os.path.isdir(folder):
            raise ValueError("The given path does not exist: " + folder)
                
        return RamFileManager.buildPath((
            folder,
            FileNames.META_DATA
        ))

    @staticmethod
    def getFileMetaData( filePath ):
        """Gets metadata for a specific file"""
        data = RamMetaDataManager.getMetaData( filePath )
        fileName = os.path.basename(filePath)
        if fileName in data:
            return data[fileName]
        return {}

    @staticmethod
    def getMetaData( folderPath ):
        """removes metadata for files which don't exist anymore and returns the data"""
        file = RamMetaDataManager.getMetaDataFile( folderPath )
        if not os.path.exists( file ):
            return {}

        data = {}
        with open(file, 'r') as f:
            content = f.read()
            try:
                data = json.loads(content)
            except:
                return {}

        folder = folderPath
        if os.path.isfile(folderPath):
            folder = os.path.dirname(folderPath)
        
        for fileName in dict(data):
            test = RamFileManager.buildPath((
                folder,
                fileName
            ))
            if not os.path.isfile(test):
                del data[fileName]
        
        
        return data

    def setFileMetaData(filePath, fileData):
        """Sets the metadata for the given file using the given dict"""
        folderPath = os.path.dirname(filePath)
        fileName = os.path.basename(filePath)
        data = RamMetaDataManager.getMetaData( folderPath )
        data[fileName] = fileData
        RamMetaDataManager.setMetaData( folderPath, data )

    @staticmethod
    def setMetaData( path, data ):
        """Sets the metadata for the given path using the given dict"""
        file = RamMetaDataManager.getMetaDataFile( path )

        with open(file, 'w') as f:
            json.dump( data, f, indent = 4)
