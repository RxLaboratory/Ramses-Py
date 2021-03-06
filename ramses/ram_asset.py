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

from . import Ramses
from .logger import log
from .ram_item import RamItem
from .constants import ItemType, Log, LogLevel
from .daemon_interface import RamDaemonInterface

# Keep the daemon at hand
daemon = RamDaemonInterface.instance()

class RamAsset( RamItem ):
    """A class representing an asset."""

    @staticmethod
    def fromDict( assetDict ):
        """Builds a RamAsset from dict like the ones returned by the RamDaemonInterface"""

        return RamAsset(
            assetDict['name'],
            assetDict['shortName'],
            assetDict['folder'],
            assetDict['group'],
            assetDict['tags']
            )

    @staticmethod
    # documented in RamItem.getFromPath()
    def fromPath( fileOrFolderPath ):
        """Returns a RamAsset instance built using the given path.
            The path can be any file or folder path from the asset
            (a version file, a preview file, etc)

        Args:
            fileOrFolderPath (str)

        Returns:
            RamAsset
        """
        asset = RamItem.fromPath( fileOrFolderPath )

        if not asset:
            return None

        if not asset.itemType() == ItemType.ASSET:
            return None

        return asset

    def __init__(self, assetName, assetShortName, assetFolder="", assetGroup="", tags=() ):
        """
        Args:
            assetName (str)
            assetShortName (str)
            assetFolder (str)
            assetGroupName (str)
            tags (list of str)
        """
        super(RamAsset, self).__init__( assetName, assetShortName, assetFolder, ItemType.ASSET, assetGroup )
        self._tags = tags

    def __updateFromDaemon(self):
        """Updates all info from what we get from the daemon"""

        if not Ramses.instance().online():
            return None

        replyDict = super(RamAsset, self).__updateFromDaemon()

        if replyDict is None:
            return None

        self._tags = replyDict['content']['tags']

        return replyDict

    def tags( self ): # Mutable
        """Some tags describing the asset. An empty list if the Daemon is not available.

        Returns:
            list of str
        """

        self.__updateFromDaemon()

        return self._tags



