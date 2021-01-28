#!/usr/bin/python

# https://stackoverflow.com/questions/42815136/how-to-read-and-print-the-contents-of-a-ttf-file
# http://www.starrhorne.com/2012/01/18/how-to-extract-font-names-from-ttf-files-using-python-and-our-old-friend-the-command-line.html
# https://www.programcreek.com/python/example/92803/fontTools.ttLib.TTFont

import datetime, io, sys, getopt, json, os, shutil
from fontTools import ttLib
from collections import OrderedDict

def removePrefix(text, prefix):
    return text[text.startswith(prefix) and len(prefix):].strip('/')

def getFamily(fRec):
    typoFamilyName = fRec['name'].getName(16, 3, 1, 1033)
    familyName = fRec['name'].getName(1, 3, 1, 1033) # FONT_SPECIFIER_FAMILY_ID=1, platformID, platEncID, langID
    family = typoFamilyName.toUnicode() if typoFamilyName else familyName.toUnicode()
    return family

def getStyle(fRec):
    typoStyleName = fRec['name'].getName(17, 3, 1, 1033)
    styleName = fRec['name'].getName(2, 3, 1, 1033)
    style = typoStyleName.toUnicode() if typoStyleName else styleName.toUnicode()
    style = "italic" if "Italic" in style.replace(" ", "") else "normal"
    return style

def getName(fRec):
    return fRec['name'].getName(4, 3, 1, 1033) # FONT_NAME_SPECIFIER_ID=4, platformID, platEncID, langID

def getWeight(rPath, ttf, fRec):
    name = getName(fRec).toUnicode().lower() # FONT_NAME_SPECIFIER_ID=4, platformID, platEncID, langID
    weight = fRec['OS/2'].usWeightClass
    weight = 'normal' if 400 == weight else 'bold' if 700 == weight else str(weight)
    fName = removePrefix(ttf, rPath)
    if weight == 'normal' and not ('regular' in name.lower() or 'italic' in name.lower() or 'regular' in fName.lower() or 'italic' in fName.lower()):
        print "Error with", ttf, "No Regular tag in font name", name, 'or file name', fName
        return -1
    if weight == 'bold' and not 'bold' in name.lower():
        print "Error with", ttf, "No Bold definer in font name", name
        return -1
    return weight

def processFiles(opts, jsonData, ttfs):
    """Get the short name from the font's names table"""
    rPath = os.path.realpath(opts["dirName"])
    for ttf in ttfs:
        with ttLib.TTFont(ttf) as fRec:
            print "Processing:", getName(fRec)
            font = OrderedDict()
            font["creationTimestamp"] = datetime.datetime.now().isoformat()
            font["font-family"] = getFamily(fRec)
            font["font-style"] = getStyle(fRec)
            font["font-weight"] = getWeight(rPath, ttf, fRec)
            font["src"] = os.path.join("/fonts/v2/", removePrefix(ttf, rPath))
            for key in font:
                if font[key] < 0:
                    return False
            jsonData['fonts'].append(font)
            #print json.dumps(jsonData, indent=4, separators=(',', ': '))
            #sys.exit(-1)
        #shutil.copy2(ttf, rPath)
    return True

def checkOpts(opts):
    if not os.path.exists(opts["dirName"]):
        print "No directory found", opts["dirName"]
        return False
    if opt["fixNames"] and not dirFixable(opts["dirName"]):
        return False
    if not forceJsonFile(opts["jsonFileName"], opts["forceJsonFile"]):
        return False
    return True

def scanTTFs(opts, rPath):
    ttfs = [tff for tff in os.listdir(rPath) if tff.endswith('.ttf')]
    if not opts["fixNames"]:
        return [os.path.join(rPath, ttf) for ttf in ttfs]
    for ttf in ttfs:
        os.rename(os.path.join(rPath, ttf), os.path.join(rPath, ttf.replace(' ', '+')))
    ttfs = [tff for tff in os.listdir(rPath) if tff.endswith('.ttf')]
    return [os.path.join(rPath, ttf) for ttf in ttfs]

def collectAndFixttfs(opts):
    rPath = os.path.realpath(opts["dirName"])
    if not os.path.exists(rPath):
        print "No directory found", rPath
        return False, []
    ttfs = scanTTFs(opts, rPath)
    if not opts["recursive"]:
        return True, ttfs
    for root, dirs, files in os.walk(rPath):
        dName = removePrefix(root, rPath)
        if ' ' in dName:
            os.rename(dr, os.path.join(rPath, dName.replace(' ', '+')))
    for root, dirs, files in os.walk(rPath):
        ttfs += scanTTFs(opts, root)
    return True, ttfs

def dumpJson(opts, jsonData):
    rPath = os.path.realpath(opts["jsonFileName"])
    if os.path.isfile(rPath):
        if not opts["forceJsonFile"]:
            print "File", rPath, "is present but no perrmission to rewrite it is given."
            return False
        if not os.access(rPath, os.W_OK):
            print "File", rPath, "is present but no not rewritable."
            return False
    with io.open(rPath, 'w') as jsonFile:
        #print json.dumps(jsonData, sort_keys=False, indent=4, separators=(',', ': '), ensure_ascii=False).decode('utf8')
        jsonFile.write(json.dumps(jsonData, sort_keys=False, indent=4, separators=(',', ': '), ensure_ascii=False).decode('utf8'))
    return True

def process(opts):
    print "Processing paramters:"
    print json.dumps(opts, sort_keys=False, indent=4, separators=(',', ': '))
    isOk, ttfs = collectAndFixttfs(opts)
    if not isOk:
        return False
    jsonData = OrderedDict()
    jsonData["creationTimestamp"] = datetime.datetime.now().isoformat()
    jsonData["version"] = opts["version"]
    jsonData["fonts"] = []
    #print json.dumps(jsonData, indent=4, separators=(',', ': '))
    #sys.exit(-1)
    if not processFiles(opts, jsonData, ttfs):
        return False
    return dumpJson(opts, jsonData)

def help():
    print 'v2.py <flag> <parameter if any> ...'
    print '-h                       this help.'
    print '-d <directory name>      process the given directory. Do not go in nesting ones.'
    print '-c <directory name>      process the given directory. Do not go in nesting ones. Fix file names as needed - default.'
    print '-r <directory name>      process the given directory. Process recursively the ones. No fixing.'
    print '-x <directory name>      process the given directory. Process recursively the ones. Fix file names and folder names as needed - default.'
    print '-o <json file name>      fonts_v2_config_cache_config.uat1.bluescape.com.json the default. If file is present operation stops.'
    print '-f <json file name>      fonts_v2_config_cache_config.uat1.bluescape.com.json the default. If file is present it is overwritten - default.'
    print '-e <json file version>   2.1 the default.'
    return

def main(argv):
    try:
        prms, args = getopt.getopt(argv,"hd:c:r:x:o:f:e",["directory=", "correct=", "recursive=", "fix", "jsonfile=", "forceJsonFile=", "jsonFileVersion="])
    except getopt.GetoptError:
        help()
        sys.exit(2)
    opts = {
        "dirName" : "./Updated_font_files_with_Dosis",
        "recursive" : True,
        "fixNames" : True,
        "jsonFileName" : "./fonts_v2_config_cache_config.uat1.bluescape.com.json",
        "forceJsonFile": True,
        "version": "2.1",
    }
    for opt, arg in prms:
        if opt == '-h':
            help()
            sys.exit()
        elif opt in ("-d", "--directory"):
            opts["dirName"] = arg
            opts["fixNames"] = False
            opts["recursive"] = False
        elif opt in ("-d", "--correct"):
            opts["dirName"] = arg
            opts["recursive"] = False
        elif opt in ("-r", "--recursive"):
            opts["dirName"] = arg
            opts["fixNames"] = False
        elif opt in ("-x", "--fix"):
            opts["dirName"] = arg
        elif opt in ("-o", "--jsonfile"):
            opts["jsonFileName"] = arg
        elif opt in ("-f", "--forceJsonFile"):
            opts["jsonFileName"] = arg
            opts["forceJsonFile"] = True
        elif opt in ("-e", "--jsonFileVersion"):
            opts["version"] = arg
        else:
            print "unsupported flag:", opt
    return process(opts)

if __name__ == "__main__":
    # execute only if run as a script
    main(sys.argv[1:])
