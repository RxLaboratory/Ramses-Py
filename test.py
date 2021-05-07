from ramses import (
    RamAsset,
    RamFileType,
    RamItem,
    RamProject,
    Ramses,
    RamShot,
    RamState,
    RamStep,
    RamUser,
    RamDaemonInterface,
    RamFileManager,
    RamSettings,
    log,
    LogLevel,
    Log
    )

import sys

def testUserClass():
    user = RamUser("Nicolas Dufresne", "Duduf", "/home/user/duduf/Ramses/Users/Duduf", 'ADMIN')

    print(user.name())
    print(user.shortName())
    print(user.role())
    print(user.folderPath())
    print(user.configPath())
    print(user.configPath(True))

def testItemClass():
    item = RamItem("Sea", "SEA", "C:/Users/Megaport/Ramses/Projects/FPE/04-ASSETS/Sets/FPE_A_SEA/FPE_A_SEA_MOD", "ASSET")

    # print(item.name())
    # print(item.shortName())
    # print(item._folderPath)
    # print(item.folderPath("MOD"))
    # print("*********")
    # print(item.currentStatus("MOD"))
    # print("*********")
    # print( item.latestVersion( "MOD", "", "WIP" ) )
    # print( item.previewFolderPath( "MOD" ) )
    # print( item.previewFilePaths( "MOD" ) )
    # print( item.publishedFolderPath( 'SHOT_PRODUCTION' ) )
    # print( item.publishedFilePaths( 'SHOT_PRODUCTION' ) )
    # print( item.versionFolderPath( 'SHOT_PRODUCTION' ) )
    # print( item.versionFilePath( 'SHOT_PRODUCTION' ) )
    # print( item.wipFolderPath( 'SHOT_PRODUCTION' ) )
    # print( item.wipFilePath( 'SHOT_PRODUCTION' ) )
    # print( item.isPublished( 'SHOT_PRODUCTION' ) )
    # print( item.setStatus( status, 'SHOT_PRODUCTION' ) )
    # print( item.status( 'SHOT_PRODUCTION' ) )
    print( item.steps() )

def testProjectClass():
    proj = RamProject("", "", "")

    print(proj.name())
    print(proj.shortName())
    # print(proj.width())
    # print(proj.height())
    # print(proj.framerate())
    print(proj._folderPath)
    print(proj.folderPath())
    # print(proj.absolutePath("05-SHOTS/PROJECTID_S_01-001"))
    # print(proj.assets("Sets"))
    print(proj.assetGroups())
    # print(proj.shots())
    # print(proj.steps())
    # print( proj.asset( "SEA" ) )
    # print( proj.shot( "004" ) )
    # print( proj.step( "RIG" ) )
    # print( proj.state( "WIP" ) )
    # print( proj.project( "MayaProd" ) )
    # print( proj.inputPipes( "inputStepShortName" ) )
    # print( proj.outputPipes( "outputStepShortName" ) )
    # print( proj.pipes() )

    #for asset in proj.assets():
    #   print( asset )
    #   print( asset.group() )

def testShotClass():
    shot = RamShot("ShotName", "ShotShortName", "J:/RAINBOX/TESTRAMSESPATH/05-SHOTS/PROJECTID_S_01-001")

    print(shot.name())
    print(shot.shortName())
    print(shot.duration())
    print(shot.getFromPath("J:/RAINBOX/TESTRAMSESPATH/05-SHOTS/PROJECTID_S_01-001/"))
    print(shot.folderPath())  # Attention RamItem pas fini donc return None

def testAssetClass():
    asset = RamAsset( "AssetName", "AssetShortName", "J:/RAINBOX/TESTRAMSESPATH/04-ASSETS/Characters/FPE_A_TRI/", "Props", ["bla", "bla"])
    other = RamAsset( "otherName", "otherShortName" )
    same = RamAsset( "AssetName", "AssetShortName" )

    print(asset.name())
    print(asset.shortName())
    print(asset.folderPath())       # Normalement, c'est OK
    print(asset.tags())
    print(asset.group())            # A VERIFIER...
    print(RamAsset.getFromPath("J:/RAINBOX/TESTRAMSESPATH/04-ASSETS/Characters/FPE_A_TRI/"))

    print ( asset )
    print ( str(asset) )


    print (asset == other) # False
    print (asset == same) # True
    print (asset != same) # False

def testStateClass():
    state = RamState("Work in progress", "WIP", 50, [255, 0, 0])

    print(state.name())
    print(state.shortName())
    print(state.completionRatio())
    print(state.color())

def testFileType():
    fileType = RamFileType("NameFichier", "ShortNameFichier", [".txt", ".py"])

    print(fileType.name())
    print(fileType.shortName())
    print(fileType.extensions())

def testRamsesMethods():
    # print( ramses.currentUser() )
    # print( ramses.currentStep() ) # => modification en cours
    # print( ramses.currentProject() )
    # print( ramses.states() )
    # print(ramses.states())
    ramses.showClient()

def testStepClass():
    step = RamStep("Modeling", "MOD", "", "PRE_PRODUCTION")
    print("=> name of the step = " + step.name())
    print("=> shortName of the step = " + step.shortName())
    print("=> commonFolderPath = " + step.commonFolderPath())
    print("=> templatesFolderPath = " + step.templatesFolderPath())
    print("=> stepType = " + step.stepType())

def testSettings():
    ramses = Ramses.instance()
    ramses.settings().ramsesClientPath = "E:/RAINBOX/LAB/DEV/02 - Applications/Ramses/Deploy/Ramses-Win/ramses.exe"
    ramses.settings().autoConnect = False
    ramses.settings().save()

def testFileManager():
    testFiles = {
        'wip': 'D:/DEV_SRC/RxOT/Ramses/Ramses/Project-Tree-Example/Project01/04-ASSETS/Characters/Projet01_A_ISOLDE/Projet01_A_ISOLDE_MOD/Projet01_A_ISOLDE_MOD.blend',
        'published': 'D:/DEV_SRC/RxOT/Ramses/Ramses/Project-Tree-Example/Project01/04-ASSETS/Characters/Projet01_A_ISOLDE/Projet01_A_ISOLDE_MOD/_published/Projet01_A_ISOLDE_MOD.abc',
        'version': 'D:/DEV_SRC/RxOT/Ramses/Ramses/Project-Tree-Example/Project01/04-ASSETS/Characters/Projet01_A_ISOLDE/Projet01_A_ISOLDE_MOD/_versions/Projet01_A_ISOLDE_MOD_test_pub002.blend',
        'general': 'D:/DEV_SRC/RxOT/Ramses/Ramses/Project-Tree-Example/Project01/04-ASSETS/Project01_G_PROD_An info file.txt',
        'missing': 'D:/DEV_SRC/RxOT/Ramses/Ramses/Project-Tree-Example/Project01/04-ASSETS/Project01_G_PROD_An info file+restored-v12+.txt',
        'restored': 'D:/DEV_SRC/RxOT/Ramses/Ramses/Project-Tree-Example/Project01/04-ASSETS/Characters/Projet01_A_ISOLDE/Projet01_A_ISOLDE_MOD/Projet01_A_ISOLDE_MOD_+restored-v10+.blend',
    }

    fm = RamFileManager
    
    for t in testFiles:
        f = testFiles[t]
        print ( "Testing " + f )
        print( fm.getSaveFilePath( f ) )
    
    asset = RamAsset.getFromPath( testFiles['wip'] ) # ok
    assetp = RamAsset.getFromPath( testFiles['published'] ) # ok
    item = RamItem.getFromPath( testFiles['wip'] ) # ok
    shot = RamShot.getFromPath( testFiles['wip'] ) # None
    itemg = RamItem.getFromPath( testFiles['general'] ) # ok

    print(asset.shortName())
    print( asset.group() )
    print(asset.folderPath())

    print( assetp.name() )

    print( item.shortName() )
    print( item.itemType() )

    print ( shot )

    print( itemg.shortName() )
    print( itemg.name() )
    print ( itemg.folderPath() )

    

RamSettings.instance().logLevel = LogLevel.DataReceived

daemon = RamDaemonInterface.instance()

# print (daemon.getAsset( "SEA" ))
# print (daemon.getCurrentStatus( "SEA", "Sea", "CD", "A" ))
# print (daemon.getProject( "MayaProd" ))
# print (daemon.getShot( "004" ))
# print (daemon.getState( "WIP" ))
# print (daemon.getStep( "RIG" ))

# testUserClass()
testItemClass()
# testProjectClass()
# testShotClass()
# testAssetClass()
# testStateClass()
# testFileType()
# testRamsesMethods()
# testStepClass()
# testSettings()
# testFileManager()

# "folder": "C:/Users/Megaport/Ramses/Projects/FPE/02-PROD/FPE_SD",
# "folder": "C:/Users/Megaport/Ramses/Projects/FPE/04-ASSETS/Characters",

