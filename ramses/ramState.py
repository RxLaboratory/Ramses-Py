from .ramObject import RamObject


class RamState( RamObject ):
    """Represents a state used in a status, like “CHK” (To be checked), “OK” (ok), “TO_DO”, etc."""

    def __init__( self, stateName, stateShortName, completionRatio=0.0 ):
        """
        Args:
            stateName (str)
            stateShortName (str)
            completionRatio (float, optional): The ratio of completion of this status
        """
        self.name = stateName
        self.shortName = stateShortName
        self.completionRatio = completionRatio

    def completionRatio( self ): #TODO
        """The ratio of completion of this state in the range [0, 100].

        Returns:
            int
        """
        pass

    def color( self ): #TODO
        """The color for this state, [R, G, B] in the range [0, 255].

        Returns:
            array of int: [255, 0, 0]
        """
        pass
