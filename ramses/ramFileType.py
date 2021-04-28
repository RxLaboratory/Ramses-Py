from .ramObject import RamObject

class RamFileType( RamObject ):
    """A File type.
    File types are typically used with RamPipe."""

    def __init__(self, name, shortname, extensions ):
        """
        Args:
            name (str)
            shortName (str)
            extensions (list of str)
        """
        super().__init__( name, shortname )
        self._extensions = extensions

    def extensions( self ):
        """The extensions which can be used for this file type, including the “.”

        Returns:
            list of string
        """
        return self._extensions