import ffmpeg
import subprocess

#ffmpeg -i temp.mp4 neki.mp3

subprocess.run('ffmpeg -i temp.mp4 neki.mp3', shell=True)
