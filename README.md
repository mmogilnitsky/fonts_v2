Author: Maxim Mogilnitsky
Email: maxim.mogilnitsky@bluescape.com
Documentation: https://confluence.common.bluescape.com/confluence/display/~maxim.mogilnitsky@bluescape.com/Font+JSON+File%2C+New+Version
Version: Alpha

Installation extras
===================
sudo pip install fontTools

Note:
from fontTools.ttLib import TTFont

Implementation
==============
The v2.py script generates a fonts.json file. The file will contain fonts with
all the essential keys. Note the links inside v2.py to the inspiring ideas and
how-tos.

In particular v2.py generates the timestamps version ID and fonts array.
All the elements are essential for various callers, like CSS. For exact details
please see the documentation link.

Examples and Explanation
-------------------------
Updated_font_files_with_Dosis offers and example folder of how to organize the
fonts. Effectively all that needs to be done is:
1. download appropriate font family from https://fonts.google.com/
2. unzip the folder into the src/destination.
    2a. If this is not a brand new creation, but an update of existing ones then
        into an existing one like Updated_font_files_with_Dosis
3. Adjust v2.py or run it with argument, see details below.
4. collect new JSON file.fonts_v2.json
    4a. Compare it with previous JSON just in case.

Note that file name fixing will be done by script *right in the supplied folder*.
Hence the orignal files might need to be copied and kept aside.

Arguments
=========
./v2.py will generate all by default.

to chenge the defaults please see:fonts_v2.json
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
        "jsonFileName" : "./fonts_v2.json",
        "forceJsonFile": True,
        "version": "2.1",
    }

To call with command line arguments other than defaults:
./v2.py -h

orfonts_v2.json

Please see help() in v2.py, for example:

def help():
    print 'v2.py <flag> <parameter if any> ...'
    print '-h                       this help.'
    print '-d <directory name>      process the given directory. Do not go in nesting ones.'
    print '-c <directory name>      process the given directory. Do not go in nesting ones. Fix file names as needed - default.'
    print '-r <directory name>      process the given directory. Process recursively the ones. No fixing.'
    print '-x <directory name>      process the given directory. Process recursively the ones. Fix file names and folder names as needed - default.'
    print '-o <json file name>      fonts_v2.json the default. If file is present operation stops.'
    print '-f <json file name>      fonts_v2.json the default. If file is present it is overwritten - default.'
    print '-e <json file version>   2.1 the default.'
    return

Extras
======

It is sometimes convinient to copy all files into the same folder, as well. For that
consider uncommenting:fonts_v2.json
def processFiles(opts, jsonData, ttfs):
    ...
        #shutil.copy2(ttf, rPath)
    return Truefonts_v2.json
fonts_v2.json
