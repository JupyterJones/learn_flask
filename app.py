#!/home/jack/Desktop/learn_flask/learn_flask/bin/python3
from flask import Flask, render_template, request
import os
import subprocess
import shutil
import datetime
import logging
import random
from PIL import Image
import glob
import time
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, Response,flash
from flask import send_file, make_response,g, jsonify
import os
import pygame
from gtts import gTTS
import time
import numpy as np
from random import randint
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
from moviepy.editor import concatenate_videoclips, AudioFileClip, TextClip
import moviepy.editor
import subprocess 
import shutil  
import subprocess




app = Flask(__name__)


# Create a logging object
logging.basicConfig(filename='myapp.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')

app = Flask(__name__, static_folder='static')


@app.route('/')
def index():
    return render_template('index.html')
@app.route('/add_effects')
def add_effects():
    return '''
        <form method="post" action="/video" enctype="multipart/form-data">
            <label for="input_video">Select input video file:</label><br>
            <input type="file" id="input_video" name="input_video"><br><br>
            <input type="submit" value="Submit">
        </form>
    '''   

@app.route('/video', methods=['POST','GET'])
def process_videos():
    DIR = "static/"
    input_video = request.files['input_video']
    ""
    # Save the uploaded video to a file
    input_video.save(f"{DIR}input_video2.mp4")
    
    command1 = f"ffmpeg -nostdin -i {DIR}input_video2.mp4 -filter:v \"minterpolate='mi_mode=mci:mc_mode=aobmc:vsbmc=1:fps=10'\" -c:v libx264 -r 20 -pix_fmt yuv420p -c:a copy -y {DIR}alice/output2.mp4"    
    subprocess.run(command1, shell=True, stderr=subprocess.PIPE, universal_newlines=True)
    
    command2 = f"ffmpeg -hide_banner -i {DIR}alice/output2.mp4 -filter:v \"setpts=5*PTS,minterpolate='fps=25:scd=none:me_mode=bidir:vsbmc=1:search_param=200'\" -t 58 -y {DIR}alice/final2.mp4"
    subprocess.run(command2, shell=True, stderr=subprocess.PIPE, universal_newlines=True)
    
    command3 = f"ffmpeg -hide_banner -i {DIR}alice/final2.mp4 -filter:v \"setpts=5*PTS,minterpolate='fps=25:scd=none:me_mode=bidir:vsbmc=1:search_param=200'\" -t 58 -y {DIR}alice/final5.mp4"
    subprocess.run(command3, shell=True, stderr=subprocess.PIPE, universal_newlines=True)

    # Add music to the video
    init = randint(10,50)
    MUSIC=["static/music/Born_a_Rockstar-Instrumental-NEFFEX.mp3","static/music/Cattle-Telecasted.mp3","static/music/Bite_Me-Clean-NEFFEX.mp3","static/music/El_Secreto-Yung_Logos.mp3","static/music/Blue_Mood-Robert_Munzinger.mp3","static/music/Escapism-Yung_Logos.mp3","static/music/Enough-NEFFEX.mp3","static/music/As_You_Fade_Away-NEFFEX.mp3","static/music/Culture-Anno_Domini_Beats.mp3","static/music/Contrast-Anno_Domini_Beats.mp3","static/music/Diving_in_Backwards-Nathan_Moore.mp3","static/music/Aztec_Empire-Jimena_Contreras.mp3","static/music/Devil_s_Organ-Jimena_Contreras.mp3","static/music/Alpha_Mission-Jimena_Contreras.mp3","static/music/Changing-NEFFEX.mp3","static/music/Anxiety-NEFFEX.mp3","static/music/6-Shots-NEFFEX.mp3","static/music/DimishedReturns.mp3","static/music/Drum_Meditation.mp3","static/music/ChrisHaugen.mp3","static/music/DoveLove-Moreira.mp3","static/music/DesertPlanet.mp3","static/music/David_Fesliyan.mp3"]
    
    music = random.choice(MUSIC)
    command3 = f"ffmpeg -i {DIR}alice/final5.mp4 -ss {init} -i {music} -af 'afade=in:st=0:d=4,afade=out:st=55:d=3' -map 0:0 -map 1:0 -shortest -y {DIR}alice/Final_End.mp4"
    subprocess.run(command3, shell=True)
    
    # Save the output video to a file   
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    shutil.copy(f"{DIR}alice/output2.mp4", f"{DIR}alice/{now}_output.mp4")
    shutil.copy(f"{DIR}alice/Final_End.mp4", f"{DIR}alice/{now}_Final.mp4")
    shutil.copy(f"{DIR}alice/Final_End.mp4", f"{DIR}alice/Final_End_mix.mp4")
    return render_template('final.html', video_file="alice/Final_End.mp4")

directories = ["static/screaming","static/abstract_beauty","static/uploads","static/experiment","static/energy_crystal"]

@app.route('/choose_dir', methods=['GET', 'POST'])
def choose_dir():
    if request.method == 'POST':
        selected_directory = request.form.get('directory')
        logging.debug("selected_directory: %s", selected_directory)
        if selected_directory is None:
            # Handle the case where no directory is selected
            logging.error("No directory selected!")
            return 'No directory selected!'
        
        # Get the list of image files in the selected directory
        logging.debug("SELECTED_DIRECTORY: %s", selected_directory)
        image_filenames = random.sample(glob.glob(selected_directory + '/*.jpg'), 30)
        im = Image.open(image_filenames[0]) 
        size = im.size
        logging.error("image_filenames: %s", image_filenames)
        image_clips = []
        for filename in image_filenames:
            # Open the image file and resize it to 512x768
            image = Image.open(filename)
            image = image.resize((size), Image.BICUBIC)
            # Convert the PIL Image object to a NumPy array
            image_array = np.array(image)
            # Create an ImageClip object from the resized image and set its duration to 1 second
            image_clip = ImageClip(image_array).set_duration(1)
        
            # Append the image clip to the list
            image_clips.append(image_clip)
    
        # Concatenate all the image clips into a single video clip
        video_clip = concatenate_videoclips(image_clips, method='compose')
        timestr = time.strftime("%Y%m%d-%H%M%S")
        # Set the fps value for the video clip
        video_clip.fps = 24
        # Write the video clip to a file
        video_file = 'static/videos/random_images' + timestr + 'Xvideo.mp4'
        output_p = 'static/videos/random_images_video.mp4'
        video_clip.write_videofile(video_file, fps=24)
        try:
            shutil.copy(video_file, output_p)
        except FileNotFoundError as e:
            logging.error("Error occurred while copying file: %s", str(e))

        ## Return a message to the client
        #return 'Video generated successfully!'

    output_p = 'static/videos/random_images_video.mp4'
    # If the request method is GET, render the form template with the list of directories
    return render_template('choose_dir.html', directories=directories, output_path=output_p)

import os
from flask import Flask, request, render_template
import subprocess
import tempfile
app = Flask(__name__)

@app.route('/add_echo_and_image_to_video', methods=['POST', 'GET'])
def add_echo_and_image_to_video():
    try:
        if request.method == 'POST':
            image = request.files['image']
            audio = request.files['audio']

            # Create temporary file paths for image and audio
            image_fd, image_path = tempfile.mkstemp(suffix=".jpg")
            audio_fd, audio_path = tempfile.mkstemp(suffix=".mp3")
            output_fd, output_path = tempfile.mkstemp(suffix=".mp3")
            os.close(image_fd)
            os.close(audio_fd)
            os.close(output_fd)

            # Save the uploaded image and audio files
            image.save(image_path)
            audio.save(audio_path)

            # Apply the echo effect using SoX
            cmd1 = (f'sox {audio_path} {output_path} reverb 60 40 100 100 0.5')

            # Run the SoX command using subprocess
            subprocess.run(cmd1, shell=True, check=True)

            # Create the video with the echo-audio and image using FFmpeg
            cmd2 = (
                f'ffmpeg -loop 1 -i {image_path} -i {output_path} '
                f'-filter_complex "[1]aecho=0.8:0.9:1000:0.3[audio_echo]" '
                f'-map 0:v -map "[audio_echo]" -c:v libx264 -tune stillimage -c:a aac -b:a 192k -pix_fmt yuv420p -shortest echo_output.mp4'
            )

            # Run the FFmpeg command using subprocess
            subprocess.run(cmd2, shell=True, check=True)

            # Remove temporary files
            os.remove(image_path)
            os.remove(audio_path)
            os.remove(output_path)

            # Render the HTML template with the video embedded
            return render_template('video_page.html', video_path='echo_output.mp4')

        else:
            return render_template('upload_page.html')  # Display the upload form for GET requests

    except Exception as e:
        return str(e)


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5100))
    app.run(debug=True, host='0.0.0.0', port=port)
