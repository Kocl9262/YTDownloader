from pytube import YouTube
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from PIL import Image, ImageTk
import requests
from io import BytesIO
import time
import ffmpeg
import os
import re
import subprocess

WINDOW_WIDTH = 515
WINDOW_HEIGHT = 550
WINDOW_TITLE = "YT Downloader"
COLOR = "#37A2DD"


class YoutubeDownloader:

    # Class to create an app that downloads youtube videos


    def __init__(self):
        self.window = tk.Tk()
        self.window.geometry("{}x{}".format(WINDOW_WIDTH, WINDOW_HEIGHT) )
        self.window.configure(bg=COLOR)
        self.window.title(WINDOW_TITLE)
        self.window.iconbitmap("icon.ico")

        IMAGE_BLANK = Image.open("tn_blank.jpg")
        IMAGE_BLANK = IMAGE_BLANK.resize((240, 135), Image.ANTIALIAS)
        PHOTO_BLANK = ImageTk.PhotoImage(IMAGE_BLANK)
        OPTIONS = ["Low Quality Video", "Audio Only (mp3)"]

        self.folder_path = tk.StringVar()
        self.OptionMenu = tk.StringVar()
        self.OptionMenu.set(OPTIONS[0])
        self.link_label = tk.Label(self.window, text = "Download Link", bg=COLOR)
        self.link_label.grid(column = 0, row = 0)
        self.load_info_button = tk.Button(self.window, text = "Load info", command = self.__get_info, width = 7)
        self.load_info_button.grid(column = 2, row = 0, sticky = "W")
        self.name_label = tk.Label(self.window, text = "Filename (empty is video name)", bg=COLOR)
        self.name_label.grid(column = 0, row = 1)
        self.select_path_button = tk.Button(self.window, text = "Set", command = self.__get_path, width = 7)
        self.select_path_button.grid(column = 2, row = 2, sticky = "W")
        self.path_label = tk.Label(self.window, text = "Download location", bg=COLOR)
        self.path_label.grid(column = 0, row = 2)
        self.ext_label = tk.Label(self.window, text = "Quality", bg=COLOR)
        self.ext_label.grid(column = 0, row = 3)
        self.link_entry = tk.Entry(master = self.window, width = 40)
        self.link_entry.grid(column = 1, row = 0)
        self.name_entry = tk.Entry(master= self.window, width = 40)
        self.name_entry.grid(column = 1, row = 1)
        self.path_entry = tk.Entry(master = self.window, width = 40, textvariable = self.folder_path)
        self.path_entry.grid(column = 1, row = 2)
        self.ext_entry = tk.OptionMenu(self.window, self.OptionMenu, *OPTIONS)
        self.ext_entry.grid(column = 1, row = 3)
        self.download_button = tk.Button(self.window, text = "Download", command = self.__get_link)
        self.download_button.grid(column = 1, row = 4)
        self.download_button.bind("<Button-1>", self.__del_done)

        self.thumbnail_label = tk.Label(self.window, image = PHOTO_BLANK)
        self.thumbnail_label.image = PHOTO_BLANK
        self.thumbnail_label.grid(column = 0, row = 5, columnspan = 2, rowspan = 5, sticky = "W")
        self.log_text = tk.Text(self.window, height = 18, width = 64)
        self.log_text.grid(column = 0, row = 11, columnspan = 3, sticky = "S")
        self.log_text.insert(tk.END, "Sebastjan's YT Downloader v1.4")
        return

    def __del_done(self, event):
        self.log_text.delete('1.0', tk.END)
        self.log_text.insert(tk.END, "Downloading...")

    def __downloader(self, link, save_path = "", save_name = "", extension = "mp4"):
        # Download video
        #try:
        yt = YouTube(link)

        # Downloads normal quality version of audio and video combined
        if extension == "Low Quality Video":
            extension = "mp4"
            yt_stream = yt.streams.filter(progressive=True, file_extension=extension).order_by('resolution').desc().first()
            yt_stream.download(output_path = save_path, filename = save_name)

        # Downloads selected video and best audio quality version and combines them
        elif extension != "Low Quality Video" and extension != "Audio Only (mp3)":
            ext = []
            ext.extend(extension.split())
            res = ext[0]
            fps = int(ext[1])
            vcodec = ext[2]

            yt_stream_video = yt.streams.filter(progressive=False, resolution=res, fps=fps, video_codec=vcodec).first()

            if yt_stream_video == None:
                self.log_text.delete('1.0', tk.END)
                self.log_text.insert(tk.END, "Video not found. \nPress 'Load info' button and select right video quality.")

            yt_stream_video.download(output_path = save_path, filename = "temp_video")
            yt_stream_audio = yt.streams.get_audio_only()
            yt_stream_audio.download(output_path = save_path, filename = "temp_audio")

            video_ext = yt_stream_video.mime_type.split("/")
            audio_ext = yt_stream_audio.mime_type.split("/")

            if save_name == "" and save_path == "":
                input_video = "temp_video." + video_ext[1]
                input_audio = "temp_audio." + audio_ext[1]

                title = re.sub(r'[\\/*?:"<>|]',"", yt.title)

                subprocess.run(f'ffmpeg -i {input_video} -i {input_audio} -c copy "{title}.mp4"', shell=True)

                os.remove("temp_video." + video_ext[1])
                os.remove("temp_audio." + audio_ext[1])

            elif save_name == "" and save_path != "":
                input_video = str(save_path) + "/temp_video." + video_ext[1]
                input_audio = str(save_path) + "/temp_audio." + audio_ext[1]

                title = re.sub(r'[\\/*?:"<>|]',"", yt.title)

                subprocess.run(f'ffmpeg -i {input_video} -i {input_audio} -c copy "{save_path}/{title}.mp4"', shell=True)

                os.remove(str(save_path) + "/temp_video." + video_ext[1])
                os.remove(str(save_path) + "/temp_audio." + audio_ext[1])

            elif save_name != "" and save_path == "":
                input_video = "temp_video." + video_ext[1]
                input_audio = "temp_audio." + audio_ext[1]

                title = re.sub(r'[\\/*?:"<>|]',"", yt.title)

                subprocess.run(f'ffmpeg -i {input_video} -i {input_audio} -c copy "{save_name}.mp4"', shell=True)

                os.remove("temp_video." + video_ext[1])
                os.remove("temp_audio." + audio_ext[1])

            elif save_name != "" and save_path != "":
                input_video = str(save_path) + "/temp_video." + video_ext[1]
                input_audio = str(save_path) + "/temp_audio." + audio_ext[1]

                title = re.sub(r'[\\/*?:"<>|]',"", yt.title)

                subprocess.run(f'ffmpeg -i {input_video} -i {input_audio} -c copy "{save_path}/{save_name}.mp4"', shell=True)

                os.remove(str(save_path) + "/temp_video." + video_ext[1])
                os.remove(str(save_path) + "/temp_audio." + audio_ext[1])

        # Downloads best audio quality version and converts it to .mp3
        elif extension == "Audio Only (mp3)":
            yt_stream = yt.streams.get_audio_only()
            yt_stream.download(output_path = save_path, filename = "temp")
            title = re.sub(r'[\\/*?:"<>|]',"", yt.title)
            # Finds where downloaded file is located
            if str(save_path):
                mp4_file = str(save_path) + "/temp.mp4"
            else:
                mp4_file = "temp.mp4"

            # Finds where converted .mp3 file must be put and how to name it
            if str(save_name) == "" and str(save_path) == "":
                mp3_file = title[:60] + ".mp3"
            elif str(save_path) == "" and str(save_name) != "":
                mp3_file = str(save_name[:60]) + ".mp3"
            elif str(save_path) != "" and str(save_name) == "":
                mp3_file = str(save_path) + "/" + title[:60] + ".mp3"
            elif str(save_name) != "" and str(save_path != ""):
                mp3_file = str(save_path) + "/" + str(save_name[:60]) + ".mp3"

            subprocess.run(f'ffmpeg -i {mp4_file} "{mp3_file}"', shell=True)

            os.remove(mp4_file)

        self.log_text.delete('1.0', tk.END)
        self.log_text.insert(tk.END, "Done!")

        """except:
            self.log_text.delete('1.0', tk.END)
            self.log_text.insert(tk.END, "Please paste valid YoutTube link in 'Download link' box")"""

        return

    def __get_path(self):
        # Set where you want to save video
        path = fd.askdirectory()
        # print(path)
        self.folder_path.set(path)
        self.log_text.delete('1.0', tk.END)
        self.log_text.insert(tk.END, "Video will be saved in '" + path + "'")

        return

    def __get_link(self):
        # Get all needed data for downloading video
        link = self.link_entry.get()
        path = self.path_entry.get()
        name = self.name_entry.get()
        ext = self.OptionMenu.get()

        self.__downloader(link, path, name, ext)

        return

    def __get_info(self):
        try:
            # Get thumbnail
            link = self.link_entry.get()
            yt = YouTube(link)
            thumbnail = yt.thumbnail_url
            response = requests.get(thumbnail)
            img_data = response.content
            img = ImageTk.PhotoImage(Image.open(BytesIO(img_data)).resize((240, 135), Image.ANTIALIAS))

            self.thumbnail_label = tk.Label(self.window, image = img)
            self.thumbnail_label.image = img
            self.thumbnail_label.grid(column = 0, row = 5, columnspan = 2, rowspan = 5, sticky = "W")

            OPTIONS = ["Low Quality Video", "Audio Only (mp3)"]

            for item in yt.streams.filter(progressive=False).order_by("resolution").desc():
                list = str(item.resolution) + " " + str(item.fps) + " " + str(item.video_codec)
                OPTIONS.append(list)

            self.ext_entry = tk.OptionMenu(self.window, self.OptionMenu, *OPTIONS)
            self.ext_entry.grid(column = 1, row = 3)

            # Get title
            title = yt.title

            # Get author
            author = yt.author

            # Get video length
            video_length = yt.length
            length = time.strftime('%H:%M:%S', time.gmtime(video_length))

            # Get view number
            views = str(yt.views)

            # Get video rating
            rating = str(yt.rating)

            # Is video age restricted
            age_restricted = yt.age_restricted

            if age_restricted == True:
                restricted = "This video is age restricted"
            else:
                restricted = "This video is not age restricted"

            # Get video ID
            id = yt.video_id

            # Get metadata
            metadata = yt.metadata

            # Get video description
            description = yt.description

            self.log_text.delete('1.0', tk.END)
            self.log_text.insert(tk.END, title + "\n\n")
            self.log_text.tag_add("title", "1.0", "1.end")
            self.log_text.tag_config("title", font = ("comic sans ms", 10, "bold"))
            self.log_text.insert(tk.END, "Channel: " + author + "\n\n")
            self.log_text.insert(tk.END, "Duration: " + length + "\n\n")
            self.log_text.insert(tk.END, "Views: " + views + "\n\n")
            self.log_text.insert(tk.END, "Rating: " + rating + "\n\n")
            self.log_text.insert(tk.END, "Video ID: " + id + "\n\n")
            self.log_text.insert(tk.END, restricted + "\n\n")
            self.log_text.insert(tk.END, "Metadata: \n\n" + str(metadata) + "\n\n")
            self.log_text.insert(tk.END, "Description: \n\n" + description + "\n\n")
        except:
            self.log_text.delete('1.0', tk.END)
            self.log_text.insert(tk.END, "Please paste valid YoutTube link in 'Download link' box")


    def run_app(self):
        self.window.mainloop()
        return


if __name__ == "__main__":
    app = YoutubeDownloader()
    app.run_app()
