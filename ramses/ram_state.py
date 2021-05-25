# -*- coding: utf-8 -*-

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
