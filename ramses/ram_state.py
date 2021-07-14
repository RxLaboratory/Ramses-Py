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

from .ram_object import RamObject

class RamState( RamObject ):
    """Represents a state used in a status, like “CHK” (To be checked), “OK” (ok), “TO_DO”, etc."""

    @staticmethod
    def fromDict( stateDict ):
        """Builds a RamState from dict like the ones returned by the RamDaemonInterface"""

        return RamState(
            stateDict['name'],
            stateDict['shortName'],
            stateDict['completionRatio'],
            stateDict['color']
            )

    def __init__(self, stateName, stateShortName, completionRatio=0, color=[67, 67, 67]):
        """
        Args:
            stateName (str)
            stateShortName (str)
            completionRatio (float, optional): The ratio of completion of this status
        """
        super(RamState, self).__init__( stateName, stateShortName )
        self._completionRatio = completionRatio
        self._color = color

    def completionRatio( self ):
        """The ratio of completion of this state in the range [0, 100].

        Returns:
            int
        """
        return self._completionRatio

    def color( self ):
        """The color for this state, [R, G, B] in the range [0, 255].

        Returns:
            array of int: [255, 0, 0]
        """
        return self._color
