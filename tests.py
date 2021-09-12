import os
from ramses.file_info import RamFileInfo
# from time import perf_counter
from ramses import (
    log,
    LogLevel,
    RamSettings,
    RamObject,
    RamState,
    RamFileType,
    RamUser,
    RamItem,
    RamMetaDataManager,
    RamFileManager,
    Ramses,
    RamStep,
    RamPipeFile,
    ItemType
    )

settings = RamSettings.instance()
settings.logLevel = LogLevel.Info

ramses = Ramses.instance()

# daemon = RamDaemonInterface.instance()

testPaths = (
    'C:/Users/Duduf/Ramses/Projects/TEST/04-ASSETS/Main Characters/TEST_A_IS/TEST_A_IS_SET/_published/AllCharas_004_CHK/TEST_A_IS_SET_AllCharas-Set.mb',
)

def ram():
    projects = Ramses.instance().projects()
    for p in projects:
        print( p )
        for step in p.steps():
            print( step )

def ramObjects():
    o = RamObject("Object Name", "OSN")
    log( o, LogLevel.Debug )
    log( RamObject.getObjectShortName(o), LogLevel.Debug )
    log( RamObject.getObjectShortName("SN"), LogLevel.Debug )
    d = { 'name': "Dict Object", 'shortName': "DO" }
    o = RamObject.fromDict( d )
    log( o, LogLevel.Debug )

def ramStates():
    s = RamState( "Test", "T", 50, [255,0,0] )
    log (s, LogLevel.Debug)

def ramFileTypes():
    ft = RamFileType("Jpeg", "jpg", ('.jpg', '.jpeg'))
    log( ft )

def ramUsers():
    u = RamUser.fromDict( {
        'name': "Nico Duf",
        'shortName': "Duduf",
        'folderPath': 'C:/Users/Duduf/Ramses/Users/Duduf',
        'role': 'ADMIN',
        'comment': ''
    })
    log( u )
    log( u.configPath() )
    u = ramses.currentUser()
    log( u )
    log( u.comment() )

def ramStep():
    step = Ramses.instance().currentProject().step('RIG')
    print(step.color())

def ramItem(pathIndex, step=''):
    print ("========FROM STRING=======")
    item = RamItem.fromString('IS | Iseult', ItemType.ASSET)
    print ("==========================")
    print(item)
    if item:
        print(item.itemType())
        print(item.folderPath())
        print(item.stepFolderPath(step))
        print(item.stepFilePaths(step))
        print(item.currentStatus(step))
        print(item.itemType())
        print(item.stepFolderPath(step))
        print(item.currentStatus())
        print(item.latestVersionFilePath('', '', step))
        print(item.versionFolderPath(step))
        print(item.projectShortName())

    print ("========FROM PATH=======")
    item = RamItem.fromPath(testPaths[pathIndex])
    print ("========================")
    print(item)
    if item:
        print(item.stepFolderPath(step))
        print(item.stepFilePaths(step))
        print(item.currentStatus(step))
        print(item.itemType())
        print(item.stepFolderPath(step))
        print(item.currentStatus())
        print(item.latestVersionFilePath(step))
        print(item.versionFolderPath(step))
        print(item.projectShortName())
        print("----------")
        print(item.latestPublishedVersionFolderPath('SET', 'TEST_A_IS_SET_AllCharas-Set.mb'))

def metadata():
    RamMetaDataManager.setComment(testPaths[1], "Test comment")
    print( RamMetaDataManager.getComment( testPaths[1] ) )

def project():
    project = ramses.project("FPE")
    print(project)
    shots = project.shots()
    for shot in shots:
        print( shot )
    
    print( project.assetGroups() )

    for asset in project.assets( ):
        print( asset )
        print( asset.itemType() )
        print( asset.group() )

    pipes = project.pipes()
    for pipe in pipes:
        for pipeFile in pipe.pipeFiles():
            print( pipeFile.getFiles( testPaths[6] ) )

def perfTest( method, numIterations=20 ):
    print('=== Perf Test Begin ===')
    start = perf_counter()
    prevIt = 0.0
    firstIt = 100000.0
    for i in range (0,numIterations):
        tic = perf_counter()
        method()
        toc = perf_counter()
        it = toc-tic
        dif = it - prevIt
        prevIt = it
        if i == 0:
            firstIt = it
        if it < 0.001:
            print(' > Iteration ' + str(i) + ' is too fast to be measured.')
            continue
        # Round
        it = int(it*1000)/1000.0
        dif = int( (dif / it)*1000 ) / 10.0
        print(' > Iteration ' + str(i) + ' took ' + str(it) + 's. (variation: ' + str(dif) + ' %)')
    end = perf_counter()
    print('=== Total Time: ' + str(int(end-start)) + ' s.' + " ===")
    if firstIt > 0.001:
        endDif = prevIt - firstIt
        endDifP = int( (endDif / firstIt)*1000 ) / 10.0
        print('=== Total Variation: ' + str(endDifP) + ' %.' + " ===")

def threadedCopy():
    bigFile1 = 'C:\\Users\\Duduf\Downloads\\ubuntu-20.04.2.0-desktop-amd64.iso'
    bigFile2 = 'D:\\SWAP\\TEMP\\ubuntu-copy.iso'
    log("Before copying")
    RamFileManager.copy(bigFile1, bigFile2)
    log("We're copying")

def fileManager():
    #print( RamFileManager.getPublishPath( 'C:\\Users\\Duduf\\Ramses\\Projects\\EXPLE\\02-PROD\\EXPLE_G_TEX\\Templates\\EXPLE_G_TEX_Template.mb' ) )
    nm = RamFileInfo()
    nm.setFileName('EXPLE_G_TEX_Template.mb')
    nm.setFileName('EXPLE_G_TEX_TEstTemplate2.mb')

def metaDataManager():
    f = 'C:/Users/Duduf/Ramses/Projects/TEST/04-ASSETS/Main Characters/TEST_A_TRI/TEST_A_TRI_MOD/_published/066_OK/TEST_A_TRI_MOD_Tristan-GeoPipe.abc'
    version = RamMetaDataManager.getVersion(f)
    state = RamMetaDataManager.getState(f)
    print('Version is: ' + str(version))
    print('State is: ' + state)

# === TESTS ===

# ramObjects()
# ramStates()
# ramFileTypes()
# ramUsers()
# ram()
ramItem(0, "MOD")
# metadata()
# project()
# threadedCopy()
# fileManager()
# metaDataManager()
# ramStep()