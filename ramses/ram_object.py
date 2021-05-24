class RamObject:
    """The base class for most of Ramses objects."""

    @staticmethod
    def fromDict( objectDict ):
        """Builds a RamObject from dict like the ones returned by the RamDaemonInterface"""

        return RamObject(
            objectDict['name'],
            objectDict['shortName']
        )

    @staticmethod
    def getObjectShortName( object ):
        from .file_manager import RamFileManager

        if isinstance( object, str ):
            shortName = object
        elif isinstance( object, RamObject ):
            shortName = object.shortName()
        else:
            raise TypeError( "Object must be a str or an instance of RamObject" )

        if not RamFileManager.validateShortName( shortName ):
            raise ValueError("This short name does not respect the Ramses naming scheme: " + shortName)

        return shortName

    def __init__( self, objectName, objectShortName ):
        """
        Args:
            objectName (str): May contain spaces, [a-z] ,[A-Z], [0-9], [+-], limited to 256 characters
            objectShortName (str):  Used for compact display and folder names, limited to 10 characters,
                must not contain spaces, may contain [a-z] ,[A-Z], [0-9], [+-].
        """

        from .file_manager import RamFileManager

        # Validate name & short name
        if not RamFileManager.validateName( objectName ):
            raise ValueError("This name does not respect the Ramses naming scheme: " + objectName)
        if not RamFileManager.validateShortName( objectShortName ):
            raise ValueError("This short name does not respect the Ramses naming scheme: " + objectShortName)

        self._name = objectName
        self._shortName = objectShortName
    
    def name( self ):
        """
        Returns:
            str
        """
        return self._name

    def shortName( self ):
        """
        Returns:
            str
        """
        return self._shortName

    def __str__( self ):
        return self._shortName + " | " + self._name

    def __eq__(self, other):
        try:
            return self._shortName == other._shortName
        except:
            return False
