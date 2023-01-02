import os
import subprocess
import cv2

# Setup
ff_path = "./ffmpeg.exe"
#in_file = "Z:\Videos\To Clean\Family Guy\S01E07 - Brian, Portrait of a Dog.mp4"
in_file = "Z:\Videos\Cleaned\Black Clover\S01E01 - Black Clover.mkv"
out_file = "S01E01_o.mkv"
out2_file = "S01E01_n.mkv"
if not os.path.exists('tmp'):
	os.mkdir("./tmp")

# get duration of film
video = cv2.VideoCapture(in_file)
duration = video.get(cv2.CAP_PROP_POS_MSEC)
frame_count = video.get(cv2.CAP_PROP_FRAME_COUNT)
print(duration , frame_count)
# Original Quality 
cmd = ff_path + ' -i \"' + in_file + '\" -ss 00:00:30 -to 00:00:50 -n ' + (".\\tmp\\" + out_file)
print(cmd)
o = subprocess.run(cmd)
# New Quality
cmd = ff_path + ' -i \"' + in_file + '\" -preset fast -c:v libx265 -c:a libvorbis -ss 00:00:27 -to 00:00:53 -n ' + (".\\tmp\\" + out2_file)
o = subprocess.run(cmd)

start = os.path.getsize('.\\tmp\\' + out_file)
end = os.path.getsize('.\\tmp\\' + out2_file)
print(start , end)
