from datetime import datetime
from .constants import LogLevel

def log( message, level = LogLevel.Info ):
    from .ram_settings import RamSettings

    message = str(message)

    minLevel = RamSettings.instance().logLevel
    if (level < minLevel ): return
    
    if level == LogLevel.DataReceived:
        message = "Ramses has just recieved some data: " + message
    elif level == LogLevel.DataSent:
        message = "Ramses has just sent some data: " + message
    elif level == LogLevel.Debug:
        message = "Debug Info from Ramses: " + message
    elif level == LogLevel.Info:
        message = "Ramses says: " + message
    elif level == LogLevel.Critical:
        message = "/!\\ Critical error, Ramses is shouting: " + message
    elif level == LogLevel.Fatal:
        message = "/!\\ Fatal error, Ramses last words are: " + message

    now = datetime.now()

    #print( "[" + now.strftime("%Y/%m/%d - %H:%M:%s") + "] " + message )
    print( message )
