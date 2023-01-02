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
#                print(out1_file , out2_file)
                try:
                        cmd = self.FFMPEG_PATH + ' -i \"' + origin + '\" -ss 00:00:30 -to 00:00:50 -n ' + ("\".\\tmp\\" + out1_file + "\"")
#                        print(cmd)
                        o = subprocess.run(cmd)
                        # New Quality
                        cmd = self.FFMPEG_PATH + ' -i \"' + origin + '\" -preset fast -c:v libx265 -c:a libvorbis -ss 00:00:27 -to 00:00:53 -n ' + ("\".\\tmp\\" + out2_file + "\"")
                        o = subprocess.run(cmd)
                        start = os.path.getsize('.\\tmp\\' + out1_file)
                        end = os.path.getsize('.\\tmp\\' + out2_file)
#                        print(start , end)
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

#                print(str(len(split)))
                if len(split) > 15: # need to fix when have , and .
                        split2 = fullLine.split('.')
#                print(split2)
                        fullpath = split2[0] + "." + split2[1][0:4]
                        newName = split2[2][6:] + "." + split2[3][0:3]
#                print(newName)
                ### Refind the subtitle list
#                print(fullpath)
#                print(newName)
#                input('here isthe list')
#                fullpath = split[0].replace("\"", "")
#                newName = split[2]

#                print(newName, fullpath)
                '''
                customArg = ['-vcodec', 'libx264', '-preset', 'fast','-vsync' , '2', '-ss', '00:00:00' ,'-to' , '00:00:30', '-tune', 'animation']
                variableRates = ['-b:v', '1M', '-maxrate', '2M', '-bufsize' , '2M']
                mapsArg = ['-map', '0:0', '-map', '0:a?', '-map', '0:s?']
                '''
                customArg = ['-preset', 'fast', '-fps_mode','vfr', '-threads', '3']
#                customArg = ['-preset', 'fast', '-fps_mode', 'vfr']
                if tune != '' and not True:
                        customArg.append('-tune')
                        customArg.append(tune)
                mapsArg = ['-map','0:v?', '-map', '0:a?', '-map', '0:s?', '-map', '0:t?']
                copyArg = ['-c:v', 'libx265','-c:a', 'libvorbis', '-c:s', 'copy', '-c:t', 'copy'] # Change this back to ssa instead of copy
#                copyArg = ['-c:v', 'libx265','-c:a', 'aac', '-c:s', 'ssa', '-c:t', 'copy'] # Change this back to ssa instead of copy
                outputFileArg = ['-y'] # Don't rewrite if already written
                if seriesName == '':
                        pass # Skip if no series name is specified
                else:
                        if not os.path.exists('./' + seriesName):
                                os.mkdir('./' + seriesName)
                        outputFileArg.append("\"" + seriesName + "\\" + newName + "\"")
#                        if ext != '.mkv': # Conversion (Might be broken)
#                                tmp = os.path.splitext(newName)
#                                outputFileArg.append(seriesName + "\\" + tmp[0] + ".mkv")
#                        else:
#                                outputFileArg.append(seriesName + "\\" + newName)
                command = self.FFMPEG_PATH + ' -i ' + fullpath + " "
#                command = [self.FFMPEG_PATH, '-i', fullpath]
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
#                command += stf(customArg) + stf(subsArg) + stf(mapsArg) + stf(metaArg)  + stf(copyArg) + stf(defaultTrack) + stf(outputFileArg).strip()
                ''' ./ffmpeg.exe -i 'NEE.mkv' -map 0:v? -map 0:a? -map 0:s? -map 0:t? -c:v libx265 -c:a libvorbis -c:s copy -c:t copy -ss 00:00:00 -to 00:00:30 -y Nee1.mkv'''
                return command
        
# Need to modify so that the folder path for the subtitle is correct right now is just file name.
''' Subtitle that works
./ffmpeg.exe -i "Z:\Videos\To Clean\The Blacklist (2013) Season 8 S08\The.Blacklist.S08E02.Katarina.Rostova.Conclusion.1080p.10bit.BluRay.AAC5.1.HEVC-Vyndros.mkv" -i "Z:\Videos\To Clean\The Blacklist (2013) Season 8 S08\The.Blacklist.S08E02.Katarina.Rostova.Conclusion.1080p.10bit.BluRay.AAC5.1.HEVC-Vyndros.srt" -map 0:v? -map 0:a? -map 0:s? -map 0:t? -c:v libx265 -c:a libvorbis -c:s copy -c:t copy -y "Blacklist\S08E02 - Katarina Rostova Conclusion.mkv"
'''

def stf(stuff):
#        print(stuff)
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
#       print(filename)
#       print(os.path.basename(filename))
#       print(filename)
        for f in curFold:
#               print(os.path.basename(f))
#               print(os.path.relpath(f))
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
#                       print(f)
                else:
                        pass
#                       print("Not a folder. Not a video. Not a valid subtitle. What are you then. Just invalid I guess")
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
#                verified = split[13]
#                replaced = split[14]
#                print(verified, replaced)
                if replaced.lower() != "true":
                        if verified.lower() == "true":
                                newSplit = l.split('.')
                                fullPath = newSplit[0] + '.' + newSplit[1][0:4]
                                file_name = newSplit[2][5:] + '.mkv\"'
#                                print(fullPath)
#                                if remux.tmpCompare(file_name.strip("\""), fullPath.strip("\"")) and False:
                                if False:
                                        print("It wouldn't help to rewrite for the file so copying")
                                        try:
#                                                print(("\"" + split[-7] + "\\" + file_name.strip("\"") + "\""))
                                                shutil.copy(fullPath.strip("\""), (split[-7] + "\\" + file_name.strip("\"")))
                                        except:
                                                print("Copying went wrong")
                                else:
                                        cmd = ""
                                        try:
                                                curName = l.split(',')[0].strip("\"")
                                                subtitles = findSubTitles(curName)
#                                                print(len(subtitles))
                                                cmd = remux.build_fmpg_cmd(l, subtitles) # Find subtitle names here
#                                                print(cmd)
                                                o = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#                                                print(o.stderr)
#                                                input("FUCK")
                                                if b'Error' in o.stderr:
                                                        pass
#                                                        print("Error occured", cmd)
#                                                        cmd['ssa'] = 'copy'
#                                                        o = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                                                elif len(o.stderr) > 100:
                                                        pass
#                                                        print(cmd)
                                        except: # Compile and print to log file the command that was used
                                                writer = ''
                                                for a in cmd:
                                                        writer += a + " "
                                                gg.write(writer)
                                                gg.write("\n")
                                                gg.flush()
#                                                print("Had problem with file", split[0])
                                                pass # Didn't work but continue

def testName():
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
#                print(l.split('.'))
#                verified = split[13]
#                replaced = split[14]
#                print(verified, replaced)
                if replaced.lower() != "true":
                        if verified.lower() == "true":
                                newSplit = l.split('.')
#                                print(l.split('.'))
                                fullPath = newSplit[0] + '.' + newSplit[1][0:4]
                                file_name = newSplit[2][5:] + '.mkv\"'
#                                print(remux.build_fmpg_cmd(l,[]))
                                remux.build_fmpg_cmd(l,[])
#                                print(fullPath)
#                                print(file_name)
#                                if not remux.tmpCompare(file_name.replace('\"', ''), fullPath.replace('\"', '')):
#                                        print("It wouldn't help to rewrite for the file so copying")
#                                else:
#                                        print("it would help")
#                                        cmd = ""

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
 #                               print(f1 , f2)
                                if os.path.getsize(f1 + "\\" + f2) > 6000 and 'mkv' in f2:
                                        rewritten.append(os.path.basename(f2))
#        print(rewritten)
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
#                print(l.strip(',').split(',')) # Uncomment Later
#                print(split[-1])
#                input()
                if split[-1].strip().lower() == "true":
                        try:
                                os.remove(split[0])
                        except:
                                print("Cannot Delete File", split[0])
                else:
                        h.write(l)
                        h.flush()
        print("Deleted files")

#s = findSubTitles("Z:\Videos\To Clean\The Blacklist (2013) Season 8 S08 (1080p BluRay x265 HEVC 10bit AAC 5.1 Vyndros)\The.Blacklist.S08E01.Roanoke.1080p.10bit.BluRay.AAC5.1.HEVC-Vyndros.mkv")
#print(s)
#print("Need to make the delimeter a extension instead of , then .")
runProgram()
cleanDatabases()
deleteRewritten()
