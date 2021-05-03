import os
from datetime import datetime

from .ramses import Ramses

class RamStatus:
    """A state associated to a comment, the user who changed the state, etc."""

    def __init__( self, state, user=None, comment="", version=0, stateDate=None, completionRatio=None ):
        """
        Args:
            state (RamState): The corresponding state.
            user (RamUser, optional): The user who created this status. Defaults to None.
            comment (str, optional): A user comment. Defaults to "".
            version (int, optional): The version of the corresponding working file. Defaults to 0.
            stateDate (datetime, optional): The date at which this status was created. Defaults to None.
            completionRatio (float, optional): The ratio of completion of this status. Defaults to None.
        """

        self.state = state
        self.completionRatio = completionRatio
        self.comment = comment
        self.version = version

        # Get J. Doe
        if not user:
            user = Ramses.instance().currentUser()
        self.user = user

        if not stateDate:
            stateDate = datetime(year = 2020, month = 1, day = 1)
        self.date = stateDate

    @staticmethod
    def getFromPath( filePath ):
        from .ramAsset import RamAsset
        from .ramShot import RamShot

        """Returns a RamStatus instance built using the given file path.

        Args:
            filePath (str)

        Returns:
            RamStatus
        """

        if not isinstance( filePath, str ):
            raise TypeError( "File path needs to be a str" )
        if not os.path.isfile( filePath ):
            filePath = Ramses.instance().currentProject().absolutePath( filePath )
            if not os.path.isfile( filePath ):
                print( "The given file could not be found" )
                return None

        baseName = os.path.basename( filePath )
        blocks = RamFileManager.decomposeRamsesFileName( baseName )
    
        if blocks == None:
            print( "The given file does not respect Ramses' naming convention" )
            return None

        version = 0
        stateId = 'WIP'

        if blocks[ "version" ] != '': # The file is already a version: gets the version info directly from it
            version = int( blocks[ "version" ] )
            if blocks[ "state" ] != '':
                stateId = blocks[ "state" ]
                stateId = stateId.upper()

        elif blocks[ "ramType" ] in ( 'A', 'S' ): # Builds a RamItem out of the given file, to then try to get its latest version info
            if blocks[ "ramType" ] == 'A':
                item = RamAsset.getFromPath( filePath )
            else:
                item = RamShot.getFromPath( filePath )

            latestVersionFilePath = item.versionFilePath( step = blocks[ "ramStep" ], resource = blocks[ "resourceStr" ] )

            if not latestVersionFilePath in (None, 0): # If it has at least one version
                latestVersionFileName = os.path.basename( latestVersionFilePath )
                latestVersionBlocks = RamFileManager.decomposeRamsesFileName( latestVersionFileName )

                version = int( latestVersionBlocks[ "version" ] )
                if latestVersionBlocks[ "state" ] != '':
                    stateId = latestVersionBlocks[ "state" ]
                    stateId = stateId.upper()

        state = Ramses.instance().state( stateId )

        dateTimeStamp = os.path.getmtime( filePath )
        dateTime = datetime.fromtimestamp( dateTimeStamp )

        status = RamStatus(state, None, "", version, dateTime)

        return status
