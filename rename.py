def atempt1():
	from unidecode import unidecode
	import pyfiglet
	result = pyfiglet.figlet_format(str(chr(8211)))
	result = pyfiglet.figlet_format('-')
	vals =[42889, 8211]
	for i in range(0, len(vals)):
		nv = (unidecode(str(chr(vals[i]))))
		try:
			print(ord(nv))
		except:
			pass

from unidecode import unidecode
def badName(filename):
	newFilename = ""
	changed = False
	for f in filename:
		if ord(f) > 255:
			nv = unidecode(str(f))
			if len(nv) > 0:
				newFilename += nv
				changed = True
			else:
				print("cannot fix", filename)
				return "NULL1"
		else:
			newFilename += f
	if changed:
		return newFilename
	else:
		return "NULL2"
import os

containingDir = "Z:\\"
fileList = []
for root, dirs, files in os.walk(containingDir):
	for name in files:
		fileList.append(os.path.join(root, name))
		newName = badName(name)
		if newName == "NULL1":
			print("Cannot Fix", name)
		elif newName == "NULL2":
			pass # no changes made
		else:
			print(name, "->" , newName)
			os.rename(os.path.join(root,name), os.path.join(root,newName))
