# -*- coding: utf-8 -*-

#====================== BEGIN GPL LICENSE BLOCK ======================
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 3
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#======================= END GPL LICENSE BLOCK ========================

import os
from datetime import datetime
from ramses.name_manager import RamNameManager

from .ramses import Ramses
from .file_manager import RamFileManager
from .logger import log
from .constants import Log, LogLevel

class RamStatus:
    """A state associated to a comment, the user who changed the state, etc."""

    @staticmethod
    def fromDict( statusDict ):
        """Builds a RamStatus from dict like the ones returned by the RamDaemonInterface"""

        state = Ramses.instance().state( statusDict['state'] )

        return RamStatus(
            state,
            statusDict['comment'],
            statusDict['completionRatio'],
            statusDict['version'],
            statusDict['user'],
            statusDict['date'],
        )

    def __init__( self, state, comment="", completionRatio=-1, version=0, user=None, stateDate=None ):
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
        if completionRatio >= 0:
            self.completionRatio = completionRatio
        else:
            self.completionRatio = state.completionRatio()
        self.comment = comment
        self.version = version

        # Get User
        if user is None:
            user = Ramses.instance().currentUser()
        self.user = user

        if stateDate is None:
            stateDate = datetime(year = 2020, month = 1, day = 1)
        if isinstance(stateDate, str):
            stateDate = datetime.strptime(stateDate, '%Y-%m-%d %H:%M:%S')
        self.date = stateDate

        self.published = False

    @staticmethod
    def fromPath( filePath ):
        from .ram_asset import RamAsset
        from .ram_shot import RamShot

        """Returns a RamStatus instance built using the given file path.

        Args:
            filePath (str)

        Returns:
            RamStatus
        """

        baseName = os.path.basename( filePath )
        nm = RamNameManager()
        if not nm.setFileName( baseName ):
            log( Log.MalformedName, LogLevel.Critical )
            return None

        version = 0
        stateId = 'WIP'

        if nm.version >= 0: # The file is already a version: gets the version info directly from it
            version = nm.version
            if nm.state != '':
                stateId = nm.state
        else:
            latestStatus = RamFileManager.getLatestVersion( filePath )
            version = latestStatus[0]
            stateId = latestStatus[1]

        state = Ramses.instance().state( stateId )

        dateTimeStamp = os.path.getmtime( filePath )
        dateTime = datetime.fromtimestamp( dateTimeStamp )

        return RamStatus(
            state,
            "",
            state.completionRatio(),
            version,
            None,
            dateTime
            )