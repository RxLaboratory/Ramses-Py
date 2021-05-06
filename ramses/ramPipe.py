class RamPipe:
    """A pipe which connects two steps together in the production pipeline.
        The pipe goes from the output step (which exports data into a specific file type)
        to the input step (which imports that data)."""

    @staticmethod
    def createFromDaemonObj( daemonReplyObj ): #TODO
        """Use this method to construct a RamPipe with an object got from the Daemon

        Args:
            daemonReplyObj (dict)

        Returns:
            RamPipe
        """
        pass

    @staticmethod
    def listFromDaemonReply( daemonReplyContent ): #TODO
        """Use this method to construct the list of RamPipe got from the Daemon reply content 
            using RamDaemonInterface.getPipes()
            This methods just loops through all objects in the list given as an argument,
            and use createFromDaemonObj(obj) on them.

        Args:
            daemonReplyContent (list)

        Returns:
            list of RamPipe
        """
        pass

    def __init__( self, inputStepShortName, outputStepShortName, fileType ):
        """

        Args:
            inputStepShortName (str)
            outputStepShortName (str)
            fileType (RamFileType)
        """
        self._inputStepShortName = inputStepShortName
        self._outputStepShortName = outputStepShortName
        self._fileType = fileType

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
            RamFileType
        """
        return self._fileType
