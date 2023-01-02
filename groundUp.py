import os
import re
from difflib import SequenceMatcher 
import random
import sys
from unidecode import unidecode

FFPROBE_PATH = './ffprobe.exe'
my_os = sys.platform
if my_os == 'linux':
	FFPROBE_PATH = '/usr/bin/ffprobe'

def longest_Substring(s1,s2):
	seq_match = SequenceMatcher(None,s1,s2) 
	match = seq_match.find_longest_match(0, len(s1), 0, len(s2)) 
	# return the longest substring 
	if (match.size!=0): 
		return (s1[match.a: match.a + match.size])  
	else:
		return ('Longest common sub-string not present')  

#containingDir = 'D:\Streams\ToEncode\\'
#containingDir = "Z:\Videos\To Clean\\"
containingDir = "Z:\Videos\\to CleanTest\\"
destinationDrive = './'

writeHeaders = not os.path.exists(containingDir + "database.csv")
headers = "fullPath,oldname,newname,extension,source,year,season,episode,seriesName,episodeName,resolution,tune,toReplace,verified,replaced\n"
loggingChanges = open(containingDir + "database.csv", "a")
dumps = open(containingDir + "dumps.csv", "a")
if writeHeaders:
	loggingChanges.write(headers)
	loggingChanges.flush()
fileRecords = []
loggingFuckups = open(containingDir + "logs.txt", "a")

# Removes parenthesis and brackets
def removePB(str):
	str = re.sub(r'\([^)]*\)', '', str)
	str = re.sub(r'\[[^]]*\]', '' , str)
	return str

def smartReplace(a, b): # Removing A from b if a is present
	a = a.lower()
	c = b.lower()
	if a in c:
		startIndex = c.index(a)
		endIndex = startIndex + len(a)
		return b[0:startIndex] + b[endIndex:]
	else:
		return b

def fullClean(line):
	split = re.split(' +', line)
	newLine = split[0] +" "
	for i in range(1, len(split)):
		addPart = True
		if split[i] == '-':
			if split[i-1] == '-':
				addPart = False
		elif split[i] == '[]' or split[i] == '()':
			addPart = False
		if i + 1 == len(split) and split[i] == '-': # Remove trailing '-'
			addPart = False
		if addPart:
			newLine += split[i] + " "
	return newLine.strip()

def removeBlacklistWords(phrase):
	blackListWords = ['x264', 'WEBRip', 'WEB-DL', 'WEB', 'Dual-Audio', 'HQ', 'BrRip','BDRip', 'Rip', 'BluRay', 'x265', 'AAC', 
				   'DVD', 'RCVR', '10bit', 'Blu-ray', 'FLAC','Dual Audio','HEVC', 'MULTI-AUDIO', 'Subbed', '10-bit', 'HDTV', 
				   'DTS-HD','Multi-Subs', 'CtrlHD', '6CH', 'AMZN', 'OPUS', 'YIFY']
	for a in blackListWords: # Removing BlacklistedWords (Upper and lowercase)
		phrase = smartReplace(a, phrase)
	fullClean(phrase)
	return phrase

# Replaces the Dots with spaces
def dotFix(filename):
	newFilename = ""
	split = filename.split(".")
	for x in split:
		x = x.strip()
		if x != "":
			newFilename += x + " "
	return newFilename.strip()

# Fixes multiple dashes at once
def dashFix(filename):
	newFilename = ""
	split = filename.split("-")
	for x in split:
		x = x.strip()
		if x != "":
			newFilename += x + " - "
	return newFilename.strip(" - ")

# Replaces non unicharacter variables
def utfFix(filename):
	for f in filename:
		if ord(f) > 255:
			nv = unidecode(str(f))
			try:
				print(str(f), str(ord(f)), str(chr(nv)))
				filename = filename.replace(f, nv)
			except:
				print("PROBLEM", str(f), str(ord(f))) 
	charmap = []
	charVal = [42889]
	for i in charVal:
		charmap.append(chr(i))
	varmap = [":"]
	for i in range(0, len(charmap)):
		filename = filename.replace(charmap[i], varmap[i])
	return filename

class fileObject:
	source = ""
	resolution = -1 # Check metadata
	newFilename = ""
	year = -1
	season = -1
	episode = -1
	endEpisode = -1
	series = ""
	episodeName = ""
	def __init__(self, filepath, subtitles):
		self.filepath = filepath
		self.fullpath = os.path.abspath(filepath)
		self.filename = os.path.basename(filepath)
		self.parentFold = os.path.dirname(filepath)
#		self.parentFold = os.path.pardir(filepath)
		self.extension = os.path.splitext(filepath)[1].strip() # Ex: .mkv
		self.subtitles = subtitles

	def getNewName(self):
		newFilename = ""
		modFilename = re.sub("\(.*?\)","",self.filename) # () Content
		modFilename = re.sub("\[.*?\]", "", modFilename) # [] Content
		modFilename = re.sub("S[0-9]+[ ]*E[0-9]+[-]*E[0-9]+","", modFilename, re.IGNORECASE) # Season and Episode
		modFilename = re.sub("S[0-9]+[ ]*E[0-9]+", "", modFilename,re.IGNORECASE) # Season and Episode Alternate Version
		modFilename = removeBlacklistWords(modFilename)
		modFilename = modFilename.replace(str(self.resolution), "") # Resolution
		if not (self.series == ""):
			modFilename = modFilename.replace(self.series, "")
		modFilename = modFilename.strip("-")
		newFilename = (newFilename + modFilename)
		if int(self.year) > 100 and int(self.year) < 3000:
			newFilename = newFilename.replace(str(self.year), "")
		newFilename = newFilename.replace(self.extension, "")
		if not (self.season == -1 or self.episode == -1): # Has season or episode Number
			preName = f'S{self.season:02d}E{self.episode:02d}'
			if not self.endEpisode == -1:
				preName += f'-E{self.endEpisode:02d}'
			newFilename = preName + " - " + newFilename
		newFilename = dotFix(newFilename)
		newFilename = dashFix(newFilename)
		# Mapping known different characters
		useUnidecode = True # Translate the values best you can to unidecode values
		if useUnidecode:
			newFilename = utfFix(newFilename)

		self.newFilename = newFilename + '.mkv'					
		return self.newFilename

	def writeToCsv(self):
		dumpData = False # Using ffprobe for dump.csv file?
		header = "fullPath,oldname,newname,extension,source,year,season,episode,seriesName,episodeName,resolution,toReplace,verified,replaced\n"
		newFilename = self.newFilename
		extension = self.extension
		if newFilename == "":
			newFilename = self.getNewName()
#		print(newFilename)
		lineWrite = "\"" + self.fullpath+ "\"," 
		lineWrite += "\""+ self.filename + "\",\"" + newFilename + "\",\"" + extension + "\"," + self.source + "," + str(self.year) + "," + str(self.season) + "," + str(self.episode) + ",\"" + self.series + "\",\"" + self.episodeName + "\"," + str(self.resolution) + ",,True,False,False\n"
		try:
			loggingChanges.write(lineWrite)
			loggingChanges.flush()
		except:
			pass
		if dumpData:
			try:
				metaDump = FFPROBE_PATH + " -i \"" + self.filename + "\" -print_format json -hide_banner"
				dumps.write(self.filename + ",\"" + metaDump + "\"\n")
				dumps.flush()
			except:
				pass

def verifyFileExtension(filename, extList):
	for x in extList:
		if x in filename:
			return True
	return False

def cleaningUp():
	acceptedExt = [".mkv", ".mov", ".mp4", '.wmv', '.m4v', '.avi', '.flv', '.srt', '.ass', '.ssa', '.sub']
	print("Starting Function to remove all files with a ._ Starting")
	fileList = []
	for root, dirs, files in os.walk(containingDir):
		for name in files:
			for x in acceptedExt:
				if x in name:
					fileList.append(os.path.join(root, name))
				if name[0:2] == "._":
					os.remove(os.path.join(root, name))
					print("Removing file "+ name)
	return fileList

def isVideoFile(filename):
	validExt = [".mkv", ".mov", ".mp4",'wmv','m4v','avi','flv']
	for x in validExt:
		if x in filename:
			return True
	return False

def isPossibleSubNames(filename, subtitleName):
	fileBaseName = os.path.relpath(filename).split(".")[0]
	subtitleNameParts = subtitleName.split(".")
	if len(subtitleNameParts) == 3: # filename.ENG.srt
		if len(subtitleNameParts[1]) == 3: # valid Subtitle name
			return True
	elif fileBaseName == subtitleNameParts[0]: # Exactly Same
		return True
	else: # Came up empty
		return False

def findSubTitles(filename):
	filename = os.path.abspath(filename)
	parentFold = os.path.dirname(filename)
	curFold = os.listdir(parentFold)
	subsList = []
	for f in curFold:
		if os.path.isdir(f):
			newDir = os.listdir(f)
			for x in newDir: # SubfolderFiles
				if os.path.isdir(x):
					loggingFuckups.write("Nested Loops with folder " + os.path.abspath(x) + "\n")
					loggingFuckups.flush()
				elif isPossibleSubNames(filename, os.path.relpath(x)):
					subsList.append(x)
		elif isVideoFile(filename):
			pass
		elif isPossibleSubNames(filename, os.path.relpath(f)):
			subsList.append(f)
		else:
			print("Not a folder. Not a video. Not a valid subtitle. What are you then. Just invalid I guess")
	return subsList

def getTags(parentDir):
	files = os.listdir(parentDir)
	filename1 = ""
	filename2 = ""
	for x in files:
		if isVideoFile(x):
			if filename1 == "":
				filename1 = x
			elif filename2 == "":
				filename2 = x
			elif int(random.random() * 10) == 5:
				if random.random() < .5:
					filename1 = x
				else:
					filename2 = x
	possibleTags = []
	actualTags = []
	split1 = filename1.split(".")
	split2 = filename1.split("[")
	split3 = filename1.split("(")
	if len(split1) > 2: # Not just filename and extension
		for x in split1:
			possibleTags.append(x)
	if len(split2) > 0: # Contains []
		for x in split2:
			if "]" in x:
				endInd = x.index("]")
				possibleTags.append(x[0:endInd])
	if len(split3) > 0: # Contains ()
		for x in split3:
			if ")" in x:
				endInd = x.index(")")
				possibleTags.append(x[0:endInd])
	# Adding the season name
	parentName = smartReplace("season", parentDir.split("\\")[-1])
	parentName = removePB(parentName)
	seriesMaybe = longest_Substring(parentName, filename1)
	
	if seriesMaybe in filename2:
		actualTags.append(seriesMaybe)
	for x in possibleTags: # Verify they can be tags
		if x in filename2:
			tag = removeBlacklistWords(x)
			actualTags.append(tag)
	return actualTags

def createFileObject(subtitles, tags, absPath):
	fileObj = fileObject(absPath, subtitles) 
	myPath3 = re.compile('S[0-9]+[ ]*E[0-9]+[-]*E[0-9]+',re.IGNORECASE).findall(absPath) # Season and Episode
	myPath4 = re.compile('S[0-9]+[ ]*E[0-9]+',re.IGNORECASE).findall(absPath) # Season and Episode Alternate Version
	if len(myPath3) == 1:
		se = []
		if "e" in myPath3[0]:
			se = myPath3[0].split("e")
		if "E" in myPath3[0]:
			se = myPath3[0].split("E")
		fileObj.season = int(se[0][1:])
		fileObj.episode = int(se[1].strip("-"))
		fileObj.endEpisode = int(se[2])
	if len(myPath4) == 1:
		se = []
		if "e" in myPath4[0]:
			se = myPath4[0].split("e")
		elif "E" in myPath4[0]:
			se = myPath4[0].split("E")
		fileObj.season = int(se[0][1:])
		fileObj.episode = int(se[1])
	resolution = re.compile('[0-9]+p', re.IGNORECASE).findall(fileObj.filename) # Resolution
	if len(resolution) == 1:
		fileObj.resolution = resolution[0]
	for x in tags: # Assigning the Tags
		possibleYears = re.compile(r'([1-2][0-9]{3})').findall(x) # Year
		known = len(resolution) == 1 or len(possibleYears) == 1 or len(myPath3) == 1 or len(myPath4) == 1
		if len(possibleYears) >= 1:
			totalPossible = re.compile(r'([1-2][0-9]{3})').findall(fileObj.filename)
			if len(totalPossible) == len(resolution) + len(possibleYears):
				if len(resolution) == 1 and resolution[0][0:-1] != possibleYears[0]:
					fileObj.year = possibleYears[0]
			else:
				if len(resolution) == 1:
					if resolution[0][0:-1] != possibleYears[0]:
						for years in totalPossible:
							if not(years == resolution[0][0:-1] or years == possibleYears[0]):
								fileObj.year = years
				else:
					for years in totalPossible:
						if years != possibleYears[0]:
							fileObj.year = years
		if not known: # Check for season
			if x in absPath and x in os.path.dirname(absPath): # Season name
				fileObj.seasonName = x
			elif fileObj.source == "":
				fileObj.source = x
	return fileObj

def extraction(curFilePath):
	curSubtitles = findSubTitles(curFilePath)
	similarTags = getTags(os.path.dirname(curFilePath))
	# Add spaces here for the periods/
	myCurFile = createFileObject(curSubtitles, similarTags, curFilePath)
#	print("Going to do the process now but modifying")
	myCurFile.getNewName()
	myCurFile.writeToCsv()
	return myCurFile

def main():
	print("Verify the FFMPEG Paths, Containing Dir and Destination Dir are correct")
#	replace = input("Would you like to do replacement? (Y, N)")
	replace = "Y"
	if "y" in replace.lower():
		os.chdir(containingDir)
		fileList = cleaningUp()
		for f in fileList:
			absCurFilePath = os.path.abspath(f)
			if isVideoFile(f):
				myCurFile = extraction(absCurFilePath)
				fileRecords.append(myCurFile)
			else:
				pass
	copyFiles = input("Would you like to copy Files? (Y, N)")
#	copyFiles = "N"
	if "y" in copyFiles.lower():
		print("Please run the other program called CopyingOver")
	print("Run through the file records and record everything while renaming")

main()
