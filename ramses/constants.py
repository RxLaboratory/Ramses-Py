class FolderNames():
    projects = "Projects"
    users = "Users"
    preview = "_preview"
    versions = "_versions"
    publish = "_published"
    userConfig = "Config"
    stepTemplates = "Templates"
    admin = "00-ADMIN"
    preProd = "01-PRE-PROD"
    prod = "02-PROD"
    postProd = "03-POST-PROD"
    assets = "04-ASSETS"
    shots = "05-SHOTS"
    export = "06-EXPORT"

class FileNames():
    META_DATA = "_ramses_data.json"

class MetaDataKeys():
    COMMENT = 'comment'

class ItemType():
    GENERAL='G'
    ASSET='A'
    SHOT='S'

class Log():
    MalformedName = "Cannot work on this file as it does not respect the Ramses' naming scheme, sorry."
    NoUser = "There's no current user. You may need to log in."
    PathNotFound = "The file or folder path could not be found."
    NoProject = "There's no current project. Select a project first."
    StateNotFound = "State not found."

class LogLevel():
    DataReceived = -2
    DataSent = -1
    Debug = 0
    Info = 1
    Critical = 2
    Fatal = 3

class StepType():
    PRE_PRODUCTION = 'PRE_PRODUCTION'
    ASSET_PRODUCTION = 'ASSET_PRODUCTION'
    SHOT_PRODUCTION = 'SHOT_PRODUCTION'
    POST_PRODUCTION = 'POST_PRODUCTION'
    ALL = 'ALL' # tous
    PRODUCTION = 'PRODUCTION' # asset and shot

class UserRole():
    STANDARD = 0
    LEAD = 1
    PROJECT_ADMIN = 2
    ADMIN = 3
