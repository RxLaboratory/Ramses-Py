import os
import re

from .ramAsset import RamAsset
from .ramItem import RamItem
from .ramObject import RamObject
from .ramses import Ramses
from .ramShot import RamShot


def getDate( e ):
    #Used in RamItem.getStepHistory to sort the list
    return e.date

def escapeRegEx( string ):
    reservedChars = "[.*+-?^=!:${|}[]\\/()"
    result = ""
    for char in string:
        if char in reservedChars:
            result = result + "\\" + char
        else:
            result = result + char
    return result


# Initialization
Ramses.instance = None

Ramses()
