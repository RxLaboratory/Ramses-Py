class RamPipe:
    """A pipe which connects two steps together in the production pipeline.
        The pipe goes from the output step (which exports data into a specific file type)
        to the input step (which imports that data)."""

    @staticmethod
    def fromDict( pipeDict ):
        """Builds a RamPipe from dict like the ones returned by the RamDaemonInterface"""

        return RamPipe(
            pipeDict['inputStepShortName'],
            pipeDict['outputStepShortName'],
            pipeDict['fileType'],
            pipeDict['colorSpace']
        )

    def __init__( self, inputStepShortName, outputStepShortName, fileType='', colorSpace='' ):
        """

        Args:
            inputStepShortName (str)
            outputStepShortName (str)
            fileType (str)
            colorSpace (str)
        """
        self._inputStepShortName = inputStepShortName
        self._outputStepShortName = outputStepShortName
        self._fileType = fileType
        self._colorSpace = colorSpace

    def inputStepShortName( self ):
        """The short name of the input step

        Returns:
            str
        """
        return self._inputStepShortName

    def outputStepShortName( self ):
        """The short name of the output step

        Returns:
            str
        """
        return self._outputStepShortName

    def fileType( self ):
        """The file type used through the pipe

        Returns:
            str
        """
        return self._fileType

    def colorSpace( self ):
        """The color space used through the pipe

        Returns:
            str
        """
        return self._colorSpace
