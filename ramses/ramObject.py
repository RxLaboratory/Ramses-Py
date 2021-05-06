class RamObject:
    """The base class for most of Ramses objects."""

    def __init__( self, objectName, objectShortName ):
        """
        Args:
            objectName (str): May contain spaces, [a-z] ,[A-Z], [0-9], [+-].
            objectShortName (str):  Used for compact display and folder names, limited to 10 characters,
                must not contain spaces, may contain [a-z] ,[A-Z], [0-9], [+-].
        """
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
            test = self._shortName == other._shortName
            return test
        except:
            print("Exception RamObject.__eq__")
