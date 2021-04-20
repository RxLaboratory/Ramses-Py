class RamObject:
    """The base class for most of Ramses objects."""

    def __init__(self, objectName, objectShortName):
        """
        Args:
            objectName (str): May contain spaces, [a-z] ,[A-Z], [0-9], [+-].
            objectShortName (str):  Used for compact display and folder names, limited to 10 characters,
                must not contain spaces, may contain [a-z] ,[A-Z], [0-9], [+-].
        """
        self.name = objectName
        self.shortName = objectShortName
    
    def name( self ):
        """
        Returns:
            str
        """
        return self.name

    def shortName( self ):
        """
        Returns:
            str
        """
        return self.shortName
