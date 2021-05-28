import os, json

from .file_manager import RamFileManager
from .constants import FileNames, MetaDataKeys

class RamMetaDataManager():
    """A Class to get/set metadata from files
    
    Ramses will use a single sidecar file in the folder where the file is contained;
    thus the metadata used by Ramses is set on a per-folder basis, and is not copied when a file is copied/moved:
    it does not make sens for Ramses to have the same metadata when a file is moved."""

    @staticmethod
    def getComment( filePath ):
        """Gets the comment for the file"""
        data = RamMetaDataManager.getFileMetaData( filePath )
        if MetaDataKeys.COMMENT in data:
            return data[MetaDataKeys.COMMENT]
        return ''

    @staticmethod
    def setComment( filePath, comment):
        """Sets a comment for the file"""
        # folder data
        data = RamMetaDataManager.getMetaData( filePath )
        fileName = os.path.basename(filePath)
        # file data
        fileData = {}
        if fileName in data:
            fileData = data[fileName]
        # update comment
        fileData[MetaDataKeys.COMMENT] = comment
        # set folder data
        data[fileName] = fileData
        RamMetaDataManager.setMetaData( filePath, data )

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
    def getMetaData( path ):
        """removes metadata for files which don't exist anymore and returns the data"""
        file = RamMetaDataManager.getMetaDataFile( path )
        if not os.path.exists( file ):
            return {}

        data = {}
        with open(file, 'r') as f:
            content = f.read()
            try:
                data = json.loads(content)
            except:
                return {}

        folder = path
        if os.path.isfile(path):
            folder = os.path.dirname(path)
        
        for fileName in dict(data):
            test = RamFileManager.buildPath((
                folder,
                fileName
            ))
            if not os.path.isfile(test):
                del data[fileName]
        
        
        return data

    @staticmethod
    def setMetaData( path, data ):
        """Sets the metadata for the given path using the given dict"""
        file = RamMetaDataManager.getMetaDataFile( path )

        with open(file, 'w') as f:
            json.dump( data, f, indent = 4)
