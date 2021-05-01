
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

def intToStr( i, numDigits=3):
    intStr = str(i)
    while len(intStr) < numDigits:
        intStr = '0' + intStr
    return intStr