from .ram_object import RamObject

class RamFileType( RamObject ):
    """A File type.
    File types are typically used with RamPipe."""

    @staticmethod
    def fromDict( fileTypeDict ):
        """Builds a RamFileType from dict like the ones returned by the RamDaemonInterface"""

        return RamFileType(
            fileTypeDict['name'],
            fileTypeDict['shortName'],
            fileTypeDict['extensions']
        )

    def __init__(self, name, shortname, extensions = () ):
        """
        Args:
            name (str)
            shortName (str)
            extensions (list of str)
        """
        super(RamFileType, self).__init__( name, shortname )
        self._extensions = extensions

    def extensions( self ):
        """The extensions which can be used for this file type, including the “.”

        Returns:
            list of string
        """
        return self._extensions
