from datetime import datetime

class Log():
    MalformedName = "Cannot work on this file as it does not respect the Ramses' naming scheme, sorry."
    NoUser = "There's no current user. You may need to log in."

class LogLevel():
    DataReceived = -2
    DataSent = -1
    Debug = 0
    Info = 1
    Critical = 2
    Fatal = 3

def log( message, level = LogLevel.Info ):
    from .ramses import Ramses
    minLevel = Ramses.instance.settings().logLevel
    if (level < minLevel ): return
    
    if level == LogLevel.DataReceived:
        message = "Ramses has just recieved some data: " + message
    elif level == LogLevel.DataSent:
        message = "Ramses has just sent some data: " + message
    elif level == LogLevel.Debug:
        message = "Ramses prints: " + message
    elif level == LogLevel.Info:
        message = "Ramses says: " + message
    elif level == LogLevel.Critical:
        message = "/!\ Critical error, Ramses is shouting: " + message
    elif level == LogLevel.Faral:
        message = "/!\ Fatal error, Ramses last words are: " + message

    now = datetime.now()

    #print( "[" + now.strftime("%Y/%m/%d - %H:%M:%s") + "] " + message )
    print( message )
