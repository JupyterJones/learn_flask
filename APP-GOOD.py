import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import subprocess
import tempfile
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
import shutil
import uuid  # Import the uuid module to generate unique filenames



app = Flask(__name__)

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
# Add other routes and functions as needed...
# For example, the 'process_videos' function from your previous code can be placed here.

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

@app.route('/add_echo_and_image_to_video', methods=['POST', 'GET'])
def add_echo_and_image_to_video():
    try:
        if request.method == 'POST':
            image = request.files['image']
            audio = request.files['audio']

            # Save the uploaded image and audio files
            image_path = 'input.jpg'
            audio_path = 'input_audio.mp3'
            image.save(image_path)
            audio.save(audio_path)

            # Apply the echo effect using SoX
            cmd1 = f'sox {audio_path} output_audio_with_reverb.mp3 reverb 60 40 100 100 0.5'
            subprocess.run(cmd1, shell=True, check=True)

            reverb ="output_audio_with_reverb.mp3"
            cmd2 = (f'ffmpeg -loop 1 -i {image_path} -i {reverb} -c:v libx264 -c:a aac -b:a 192k -pix_fmt yuv420p -shortest echo_output.mp4'
            )
            print("COMMAND2", cmd2)
            subprocess.run(cmd2, shell=True, check=True)

            # Remove intermediate audio file
            #os.remove('output_audio_with_reverb.mp3')

            # Generate a unique filename for the output video
            unique_filename = str(uuid.uuid4()) + '.mp4'
            # Move the output video to the static folder
            shutil.move('echo_output.mp4', os.path.join('static', unique_filename))

            # Return the unique filename to the client for download
            return unique_filename

        else:
            return render_template('upload_page.html')  # Display the upload form for GET requests

    except Exception as e:
        return str(e)


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5100))
    app.run(debug=True, host='0.0.0.0', port=port)