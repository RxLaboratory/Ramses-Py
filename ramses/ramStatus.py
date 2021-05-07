import os
from datetime import datetime

from .ramses import Ramses
from .file_manager import RamFileManager
from .ramSettings import RamSettings
from .logger import log, Log, LogLevel

class RamStatus:
    """A state associated to a comment, the user who changed the state, etc."""

    @staticmethod
    def fromDict( statusDict ):
        """Builds a RamStatus from dict like the ones returned by the RamDaemonInterface"""

        s = RamStatus(
            statusDict['state'],
            statusDict['user'],
            statusDict['comment'],
            statusDict['version'],
            statusDict['date'],
            statusDict['completionRatio']
        )
        return s

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
    def fromPath( filePath ):
        from .ramAsset import RamAsset
        from .ramShot import RamShot

        """Returns a RamStatus instance built using the given file path.

        Args:
            filePath (str)

        Returns:
            RamStatus
        """

        baseName = os.path.basename( filePath )
        blocks = RamFileManager.decomposeRamsesFileName( baseName )
    
        if blocks is None:
            log( Log.MalformedName, LogLevel.Critical )
            return None

        version = 0
        stateId = 'WIP'

        if blocks[ "version" ] >= 0: # The file is already a version: gets the version info directly from it
            version =blocks[ "version" ]
            if blocks[ "state" ] != '':
                stateId = blocks[ "state" ]
                stateId = stateId.upper()

        else:
            latestStatus = getLatestVersion( filePath )
            version = latestStatus[0]
            stateId = latestStatus[1]

        state = Ramses.instance().state( stateId )

        dateTimeStamp = os.path.getmtime( filePath )
        dateTime = datetime.fromtimestamp( dateTimeStamp )

        status = RamStatus( state,
            "",
            state.completionRatio(),
            version,
            None,
            dateTime
            )

        return status
