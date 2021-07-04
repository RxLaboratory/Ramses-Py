# -*- coding: utf-8 -*-

from .ram_pipefile import RamPipeFile

class RamPipe:
    """A pipe which connects two steps together in the production pipeline.
        The pipe goes from the output step (which exports data into a specific file type)
        to the input step (which imports that data)."""

    @staticmethod
    def fromDict( pipeDict ):
        """Builds a RamPipe from dict like the ones returned by the RamDaemonInterface"""

        pipeFiles = []

        if 'pipeFiles' in pipeDict:
            for pipe in pipeDict['pipeFiles']:
                pipeFiles.append(
                    RamPipeFile.fromDict(pipe)
                )

        return RamPipe(
            pipeDict['inputStepShortName'],
            pipeDict['outputStepShortName'],
            pipeFiles
        )

    def __init__( self, inputStepShortName, outputStepShortName, pipeFiles ):
        """

        Args:
            inputStepShortName (str)
            outputStepShortName (str)
            fileType (str)
            colorSpace (str)
        """
        self._inputStepShortName = inputStepShortName
        self._outputStepShortName = outputStepShortName
        self._pipeFiles = pipeFiles

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

    def pipeFiles( self ):
        return self._pipeFiles