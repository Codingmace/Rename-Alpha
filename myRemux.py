import subprocess
import os
import sys

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

        def build_ffprobe_cmd(self, source):
                command = self.FFPROBE_PATH + " \"" + source + "\" -hide_banner -pretty"
                return command

        def build_fmpg_cmd(self,split, subtitleList):
                fullpath = split[0].replace("\"", "")
                oldname = split[1]
                newName = split[2]
                ext = split[3]
                source = split[4]
                year = split[5]
                season = split[6]
                episode = split[7]
                seriesName = split[8]
                episodeName = split[9]
                resolution = split[10]
                tune = split[11]
                '''
                customArguments = ['-vcodec', 'libx264', '-preset', 'fast','-vsync' , '2', '-ss', '00:00:00' ,'-to' , '00:00:30', '-tune', 'animation']
                variableRates = ['-b:v', '1M', '-maxrate', '2M', '-bufsize' , '2M']
                mapsArgument = ['-map', '0:0', '-map', '0:a?', '-map', '0:s?']
                '''
                customArguments = ['-preset', 'fast', '-vsync','vfr']
                if tune != '' and not True:
                        customArguments.append('-tune')
                        customArguments.append(tune)
                mapsArgument = ['-map','0:v?', '-map', '0:a?', '-map', '0:s?', '-map', '0:t?']
                copyArguments = ['-c:v', 'libx265','-c:a', 'aac', '-c:s', 'copy', '-c:t', 'copy'] # Change this back to ssa instead of copy
#                copyArguments = ['-c:v', 'libx265','-c:a', 'aac', '-c:s', 'ssa', '-c:t', 'copy'] # Change this back to ssa instead of copy
                outputFileArguments = ['-y']
                if seriesName == '':
                        pass # Skip if no series name is specified
                else:
                        if not os.path.exists('./' + seriesName):
                                os.mkdir('./' + seriesName)
                        if ext != '.mkv': # Conversion (Might be broken)
                                tmp = os.path.splitext(newName)
                                outputFileArguments.append(seriesName + "\\" + tmp[0] + ".mkv")
                        else:
                                outputFileArguments.append(seriesName + "\\" + newName)
                command = [self.FFMPEG_PATH, '-i', fullpath]
                subsArgument = []
                metaArgument = []
                defaultTrack = []
                if int(year) > 1970:
                        metaArgument.append('-metadata')
                        metaArgument.append("year=" + str(year))
                if tune != '' and not True:
                        customArguments.append('-tune')
                        customArguments.append(tune)
                if resolution != -1:
                        customArguments.append('-vf')
                        customArguments.append("scale=-1:" + resolution.replace("p","").replace("P", ""))
                for index, subtitle in enumerate(subtitleList):
                        mapsArgument += ['-map', str(index + 1) + ':0'] # Is this the old arguements?
                        subsArgument += ['-i', subtitle]
                        # check if subtitle has language before extension
                        subNameSplitted = subtitle.split('.')
                        subNameSplitted.pop(-1)
                        language = subNameSplitted[-1]
                        metaArgument += ['-metadata:s:s:' + str(index), 'language=' + language]
                        if (self.LANGUAGE_DEFAULT in language):
                                defaultTrack = ['-disposition:s:' + str(index), 'default']
                command +=  customArguments + subsArgument + mapsArgument + metaArgument  + copyArguments + defaultTrack + outputFileArguments
                ''' ./ffmpeg.exe -i 'NEE.mkv' -map 0:0 -map 0:a? -map 0:s? -map 0:t? -c:v libx265 -c:a aac -c:s ssa -c:t copy -ss 00:00:00 -to 00:00:30 -y Nee1.mkv'''
                return command

containDir = "./" # Changeable Variable
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
                split = l.split(',')
                verified = split[13]
                replaced = split[14]
                if replaced.lower() != "true":
                        if verified.lower() == "true":
                                cmd = remux.build_fmpg_cmd(split, [])
                                try:
                                        o = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                                        if b'Error' in o.stderr:
                                                print("Error occured")
                                                cmd['ssa'] = 'copy'
                                                o = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                                        elif len(o.stderr) > 100:
                                                print(cmd)
                                except: # Compile and print to log file the command that was used
                                        writer = ''
                                        for a in cmd:
                                                writer += a + " "
                                        gg.write(writer)
                                        gg.write("\n")
                                        gg.flush()
                                        print("Had problem with file", split[0])
                                        pass # Didn't work but continue

# Add the sub folders
# Skip for now
def cleanDatabase(dest_fold): # After running this you will need to rename the files to match the new file
        print("Going through database.csv and writting an updated version to database1.csv")
        files = os.listdir(dest_fold)
        g = open(containDir + 'database.csv','r')
        lines = g.readlines()
        rewritten = []
        for fa in files:
                f = dest_fold + fa
                if os.path.getsize(f) > 100: # Replaced sucessfully
                        # Verify the codex are correct
                        rewritten.append(os.path.basename(fa))
        for o in range(0, len(lines)):
                l = lines[o]
                split = l.split(',')
                name = split[2]
                if ".mp4" in name:
                        name = name.replace('.mp4', '.mkv')
                ind = -1
                for i in range(0, len(rewritten)):
                        if rewritten[i] == name:
                                ind = i
                if ind != -1:
                        print(lines[o])
                        lines[o] = lines[o].replace("False", "True")
        h = open(containDir + 'database1.csv', 'w')
        h.writelines(lines)
        h.flush()

# This will remove the files that are all maked True. Do not use unless know what you are doing
def deleteRewritten(): # Then the database file will be called left so renaming is needed
        f = open(containDir + "database.csv", "r")
        g = open(containDir + 'left.csv', 'w')
        lines = f.readlines()
        print("Rewritting the files from database.csv to left.csv")
        for l in lines:
                split = l.strip().strip(',').split(',')
                if split[-1].strip().lower() == "true":
                        try:
                                os.remove(split[0])
                        except:
                                print("Cannot Delete File", split[0])
                else:
                        g.write(l)
                        g.flush()

runProgram()
#currentFolder = "./Stream/" # Changable Variable
#cleanDatabase(currentFolder)
#deleteRewritten()
