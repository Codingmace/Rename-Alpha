import subprocess
import os
import sys
import shutil


class Remux:

        def __init__(self):
                self.FFMPEG_PATH = './ffmpeg.exe'
                self.FFPROBE_PATH = './ffprobe.exe'
                self.LANGUAGE_DEFAULT = "eng"
                my_os = sys.platform
                if my_os == 'linux':
                        self.FFMPEG_PATH = '/usr/bin/ffmpeg'
                        self.FFPROBE_PATH = '/usr/bin/ffprobe'
                self.DEST_FILE_FORMAT = "mine1.mkv" # Format of the name Not
                self.dest_fold = './'

        def tmpCompare(self, in_file, origin):
                if 'mkv' not in in_file:
                        return False
                out1_file = in_file.replace('.mkv', '_o.mkv') # original file
                out2_file = in_file.replace('.mkv', '_n.mkv') # New version
                if not os.path.exists('tmp'):
                        os.mkdir("./tmp")
                try:
                        cmd = self.FFMPEG_PATH + ' -i \"' + origin + '\" -ss 00:00:30 -to 00:00:50 -n ' + ("\".\\tmp\\" + out1_file + "\"")
                        o = subprocess.run(cmd)
                        # New Quality
                        cmd = self.FFMPEG_PATH + ' -i \"' + origin + '\" -preset fast -c:v libx265 -c:a libvorbis -ss 00:00:27 -to 00:00:53 -n ' + ("\".\\tmp\\" + out2_file + "\"")
                        o = subprocess.run(cmd)
                        start = os.path.getsize('.\\tmp\\' + out1_file)
                        end = os.path.getsize('.\\tmp\\' + out2_file)
                        return (start / end) > 1.1
                except:
                        print("Something went wrong")
                        return False
                return False


        def build_fmpg_cmd(self,fullLine, subtitleList):
                split = fullLine.split(',')
                fullpath = "\"" + split[0] + "\""
                newName = split[2]
                ext = split[-12]
                source = split[-11]
                year = split[-10]
                season = split[-9]
                episode = split[-8]
                seriesName = split[-7]
                episodeName = split[-6]
                resolution = split[-5]
                tune = split[-4]

                if len(split) > 15: # need to fix when have , and .
                        split2 = fullLine.split('.')
                        fullpath = split2[0] + "." + split2[1][0:4]
                        newName = split2[2][6:] + "." + split2[3][0:3]
#                customArg = ['-preset', 'fast', '-fps_mode','vfr', '-threads', '3']
                customArg = ['-preset', 'fast', '-fps_mode','vfr']
                if tune != '' and not True:
                        customArg.append('-tune')
                        customArg.append(tune)
                mapsArg = ['-map','0:v:0', '-map', '0:a?', '-map', '0:s?', '-map', '0:t?']
                copyArg = ['-c:v', 'libx265','-c:a', 'libvorbis', '-c:s', 'copy', '-c:t', 'copy'] # Change this back to ssa instead of copy
#                copyArg = ['-c:v', 'libx265','-c:a', 'libvorbis', '-c:s', 'srt', '-c:t', 'copy'] # Change this back to ssa instead of copy
                outputFileArg = ['-y'] # Don't rewrite if already written
                if seriesName == '':
                        pass # Skip if no series name is specified
                else:
                        if not os.path.exists('./' + seriesName):
                                os.mkdir('./' + seriesName)
                        outputFileArg.append("\"" + seriesName + "\\" + newName + "\"")
                command = self.FFMPEG_PATH + ' -i ' + fullpath + " "
                subsArg = []
                metaArg = []
                defaultTrack = []
                if int(year) > 1970:
                        metaArg.append('-metadata')
                        metaArg.append("year=" + str(year))
                if tune != '' and not True:
                        customArg.append('-tune')
                        customArg.append(tune)
                if resolution != -1 and not True:
                        customArg.append('-vf')
                        customArg.append("scale=-1:" + resolution.replace("p","").replace("P", ""))
                for index, subtitle in enumerate(subtitleList):
                        mapsArg += ['-map', str(index + 1) + ':0'] # Is this the old arguements?
                        fullSubs = "\"" + split[0][0:split[0].rindex("\\") + 1] + subtitle + "\""
                        subsArg += ['-i', fullSubs]
                        # check if subtitle has language before extension
                        subNameSplitted = subtitle.split('.')
                        subNameSplitted.pop(-1)
                        language = subNameSplitted[-1]
                        metaArg += ['-metadata:s:s:' + str(index), 'language=' + language]
                        if (self.LANGUAGE_DEFAULT in language):
                                defaultTrack = ['-disposition:s:' + str(index), 'default']
                command += stf(subsArg) + stf(customArg) + stf(mapsArg) + stf(metaArg)  + stf(copyArg) + stf(defaultTrack) + stf(outputFileArg).strip()
                print(command)
                return command
        
def stf(stuff):
        tmp = ""
        for s in stuff:
                tmp += s + ' '
        return tmp

def isVideoFile(filename):
        validExt = [".mkv", ".mov", ".mp4",'wmv','m4v','avi','flv']
        for x in validExt:
                if x in filename:
                        return True
        return False

def isPossibleSubNames(filename, subtitleName):
        fileBaseName = os.path.relpath(filename).split(".")[0:-1]
        subtitleNameParts = subtitleName.split(".")
        if len(subtitleNameParts) == 3: # filename.ENG.srt
                if len(subtitleNameParts[1]) == 3: # valid Subtitle name
                        return True
        elif fileBaseName == subtitleNameParts[:-1]: # Exactly Same
                return True
        else: # Came up empty
                return False

def findSubTitles(filename):
        parentFold = os.path.dirname(filename)
        curFold = os.listdir(parentFold)
        filename = os.path.basename(filename)
        subsList = []
        for f in curFold:
                if os.path.isdir(f):
                        newDir = os.listdir(f)
                        for x in newDir: # SubfolderFiles
                                if os.path.isdir(x):
                                        loggingFuckups.write("Nested Loops with folder " + os.path.abspath(x) + "\n")
                                        loggingFuckups.flush()
                                elif isPossibleSubNames(filename, os.path.basename(x)):
                                        subsList.append(x)
                elif isVideoFile(f):
                        pass
                elif isPossibleSubNames(filename, os.path.basename(f)):
                        subsList.append(f)
                else:
                        pass
        return subsList

containDir = "./" # Changeable Variable
# need to fix subtitles
gg = open("logs.txt",'w')
def runProgram():
        f = open(containDir + 'database.csv', 'r')
        lines = f.readlines()
        info = "Y"
#       info = input("Are all " + str(lines) + " lines in the excel correct (Y or N)")
        if info.lower() == 'n':
                print('That is a problem. Rerun later')
                return
        remux = Remux()
        for l in lines:
                split = l.split(',') # Change to acccount for , in the names
                verified = split[-2]
                replaced = split[-1]
                if replaced.lower() != "true":
                        if verified.lower() == "true":
                                newSplit = l.split('.')
                                fullPath = newSplit[0] + '.' + newSplit[1][0:4]
                                file_name = newSplit[2][5:] + '.mkv\"'
                                if False:
                                        print("It wouldn't help to rewrite for the file so copying")
                                        try:
                                                shutil.copy(fullPath.strip("\""), (split[-7] + "\\" + file_name.strip("\"")))
                                        except:
                                                print("Copying went wrong")
                                else:
                                        cmd = ""
                                        try:
                                                curName = l.split(',')[0].strip("\"")
                                                subtitles = findSubTitles(curName)
                                                cmd = remux.build_fmpg_cmd(l, subtitles) # Find subtitle names here
                                                o = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                                                if b'Error' in o.stderr:
                                                        pass
                                                elif len(o.stderr) > 100:
                                                        pass
                                        except: # Compile and print to log file the command that was used
                                                writer = ''
                                                for a in cmd:
                                                        writer += a + " "
                                                gg.write(writer)
                                                gg.write("\n")
                                                gg.flush()
                                                pass # Didn't work but continue

def testName():
        f = open(containDir + 'database.csv', 'r')
        lines = f.readlines()
        info = "Y"
        if info.lower() == 'n':
                print('That is a problem. Rerun later')
                return
        remux = Remux()
        for l in lines:
                split = l.split(',') # Change to acccount for , in the names
                verified = split[-2]
                replaced = split[-1]
                if replaced.lower() != "true":
                        if verified.lower() == "true":
                                newSplit = l.split('.')
#                                print(l.split('.'))
                                fullPath = newSplit[0] + '.' + newSplit[1][0:4]
                                file_name = newSplit[2][5:] + '.mkv\"'
                                remux.build_fmpg_cmd(l,[])

# Changes last field to the files that have been rewritten
# Need to fix for the files with ','
def cleanDatabases():
        # Copying over to rewrite the database
        i = 1
        while os.path.exists(('database_' + str(i) + '.csv')):
                i += 1
        newFile = ('database_' + str(i) + '.csv')
        shutil.copy('database.csv', newFile)
        folds = []
        files1 = os.listdir('./')
        rewritten = []
        for f1 in files1:
                if os.path.isdir(f1):
                        files2 = os.listdir(f1)
                        for f2 in files2: # Verify these are working
                                if os.path.getsize(f1 + "\\" + f2) > 6000 and 'mkv' in f2:
                                        rewritten.append(os.path.basename(f2))
        g = open(newFile , 'r')
        h = open('database.csv' ,'w')
        lines = g.readlines()
        for o in range(0, len(lines)):
                l = lines[o]
                split = l.split(',')
                name = split[2]
                ind = -1
                for i in range(0, len(rewritten)):
                        if rewritten[i] == name:
                                ind = i
                if ind != -1:
                        print(lines[o])
                        lines[o] = lines[o].replace("False", "True")
        h.writelines(lines)
        h.flush()
        h.close()

# Delete the old files that have been repllace and update hte database
def deleteRewritten():
        i = 1
        while os.path.exists(('database_' + str(i) + '.csv')):
                i += 1
        newFile = ('database_' + str(i) + '.csv')
        shutil.copy('database.csv', newFile)
        g = open(newFile , 'r')
        h = open('database.csv' ,'w')
        lines = g.readlines()
        for l in lines:
                split = l.strip().strip(',').split(',')
                if split[-1].strip().lower() == "true":
                        try:
                                os.remove(split[0])
                        except:
                                print("Cannot Delete File", split[0])
                else:
                        h.write(l)
                        h.flush()
        print("Deleted files")


runProgram()
cleanDatabases()
deleteRewritten()
