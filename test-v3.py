from ramses import (
    log,
    LogLevel,
    RamObject
    )

# RamSettings.instance().logLevel = LogLevel.DataReceived

# daemon = RamDaemonInterface.instance()
# settings = RamSettings.instance()

testPaths = (
    'C:/Users/Duduf/Ramses/Projects/FPE/02-PROD/FPE_G_MOD',
)

def ramObjects():
    o = RamObject("Object Name", "OSN")
    log( o )
    log( RamObject.getObjectShortName(o) )
    log( RamObject.getObjectShortName("SN"))
    d = { 'name': "Dict Object", 'shortName': "DO" }
    o = RamObject.fromDict( d )
    log( o )

ramObjects()