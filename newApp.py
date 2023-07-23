import os
from flask import Flask, render_template, request, send_file
import subprocess
import shutil
import os
from flask import Flask, render_template, request, send_from_directory
import subprocess
import shutil
import uuid  # Import the uuid module to generate unique filenames

app = Flask(__name__)

@app.route('/')
def index2():
    return render_template('index2.html')

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

            # Create the video with the echo-audio and image using FFmpeg
            #cmd2 = (
            #    f'ffmpeg -loop 1 -i {image_path} -i output_audio_with_reverb.mp3 '
            #    f'-filter_complex "[1]aecho=0.8:0.9:1000:0.3[audio_echo]" '
            #    f'-map 0:v -map "[audio_echo]" -c:v libx264 -tune stillimage -c:a aac -b:a 192k -pix_fmt yuv420p -shortest #echo_output.mp4'
            #)
            #subprocess.run(cmd2, shell=True, check=True)
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
