from ramses import (RamAsset, RamFileType, RamItem, RamProject, Ramses,
                    RamShot, RamState, RamStep, RamUser)


def testUserClass():
    user = RamUser("Nicolas Dufresne", "Duduf", "/home/user/duduf/Ramses/Users/Duduf", 'ADMIN')

    print(user.name())
    print(user.shortName())
    print(user.role())
    print(user.folderPath())
    print(user.configPath())
    print(user.configPath(True))


def testItemClass():
    item = RamItem("Tristan", "TRI", "ASSET")

    print(item.name())
    print(item.shortName())
    print(item._folderPath)
    print( item.currentStatus( 'SHOT_PRODUCTION' ) )
    # print( item.latestVersion( 'SHOT_PRODUCTION' ) )
    # print( item.previewFolderPath( 'SHOT_PRODUCTION' ) )
    # print( item.previewFilePaths( 'SHOT_PRODUCTION' ) )
    # print( item.publishedFolderPath( 'SHOT_PRODUCTION' ) )
    # print( item.publishedFilePaths( 'SHOT_PRODUCTION' ) )
    # print( item.versionFolderPath( 'SHOT_PRODUCTION' ) )
    # print( item.versionFilePath( 'SHOT_PRODUCTION' ) )
    # print( item.wipFolderPath( 'SHOT_PRODUCTION' ) )
    # print( item.wipFilePath( 'SHOT_PRODUCTION' ) )
    # print( item.isPublished( 'SHOT_PRODUCTION' ) )
    # print( item.setStatus( status, 'SHOT_PRODUCTION' ) )
    # print( item.status( 'SHOT_PRODUCTION' ) )


def testProjectClass():
    proj = RamProject("ProjectName", "ProjectShortName", "/home/user/duduf/Ramses/Users/Duduf", 1920, 1080, 5.8)

    print(proj.name())
    print(proj.shortName())
    print(proj._folderPath)
    # print( proj.absolutePath( relativePath ) )
    print(proj.assets("Sets"))
    print(proj.assetGroups())
    print(proj.shots())
    print(proj.steps("SHOT_PRODUCTION"))


def testShotClass():
    shot = RamShot("ShotName", "ShotShortName", "J:/RAINBOX/TESTRAMSESPATH/05-SHOTS/PROJECTID_S_01-001")

    print(shot.name())
    print(shot.shortName())
    print(shot.duration())
    print(shot.getFromPath("J:/RAINBOX/TESTRAMSESPATH/05-SHOTS/PROJECTID_S_01-001/"))
    print(shot.folderPath())  # Attention RamItem pas fini donc return None


def testAssetClass():
    asset = RamAsset("AssetName", "AssetShortName", "J:/RAINBOX/TESTRAMSESPATH/04-ASSETS/", "Props", ["bla", "bla"])

    print(asset.name())
    print(asset.shortName())
    print(asset.folderPath())  # Attention RamItem pas fini donc return None
    print(asset.tags())
    print(asset.group())
    print(asset.getFromPath("J:/RAINBOX/TESTRAMSESPATH/04-ASSETS/Characters/FPE_A_TRI/"))


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
    ramses = Ramses.instance
    # print( ramses.currentUser() )
    # print( ramses.currentStep() ) # => modification en cours
    # print( ramses.currentProject() )
    print(ramses.states())


def testStepClass():
    step = RamStep("Modeling", "MOD", "", "PRE_PRODUCTION")

    print( "=> name of the step = " + step.name() )
    print( "=> shortName of the step = " + step.shortName() )
    print( "=> commonFolderPath = " + step.commonFolderPath() )
    print( "=> templatesFolderPath = " + step.templatesFolderPath() )
    print( "=> stepType = " + step.stepType() )


# testUserClass()
# testItemClass()
# testProjectClass()
# testShotClass()
# testAssetClass()
# testStateClass()
# testFileType()
# testRamsesMethods()
testStepClass()

# "folder": "C:/Users/Megaport/Ramses/Projects/FPE/02-PROD/FPE_SD",
# "folder": "C:/Users/Megaport/Ramses/Projects/FPE/04-ASSETS/Characters",
