import time
import os
import tempfile
import zipfile
import platform
import subprocess
from moviepy.editor import (AudioFileClip, CompositeVideoClip, CompositeAudioClip, ImageClip,
                            TextClip, VideoFileClip)
from moviepy.audio.fx.audio_loop import audio_loop
from moviepy.audio.fx.audio_normalize import audio_normalize
import requests

def download_file(url, filename):
    with open(filename, 'wb') as f:
        headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        f.write(response.content)

def search_program(program_name):
    try: 
        search_cmd = "where" if platform.system() == "Windows" else "which"
        return subprocess.check_output([search_cmd, program_name]).decode().strip()
    except subprocess.CalledProcessError:
        return None

def get_program_path(program_name):
    program_path = search_program(program_name)
    return program_path

def get_output_media(audio_file_path, timed_captions, background_video_data, video_server):
    OUTPUT_FILE_NAME = "rendered_video.mp4"
    TARGET_SIZE = (1080, 1920)  # Portrait resolution

    # Setup ImageMagick for TextClip rendering
    magick_path = get_program_path("magick")
    os.environ['IMAGEMAGICK_BINARY'] = magick_path if magick_path else '/usr/bin/convert'

    visual_clips = []
    temp_video_paths = []  # Track for cleanup

    # Process video clips
    for (t1, t2), video_url in background_video_data:
        temp_video = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        temp_video_paths.append(temp_video.name)
        download_file(video_url, temp_video.name)

        clip = VideoFileClip(temp_video.name).subclip(0, min(t2 - t1, VideoFileClip(temp_video.name).duration))
        clip = clip.resize(height=TARGET_SIZE[1]).crop(width=TARGET_SIZE[0], x_center=clip.w / 2)
        clip = clip.set_start(t1).set_end(t2)
        visual_clips.append(clip)

    # Add text captions
    for (t1, t2), text in timed_captions:
        txt_clip = TextClip(txt=text, fontsize=70, color="yellow", stroke_width=0,
                            stroke_color="None", method="label", size=(1000, None))
        txt_clip = txt_clip.set_position(("center", TARGET_SIZE[1] - 300)).set_start(t1).set_end(t2)
        visual_clips.append(txt_clip)

    # Set up audio
    audio_clip = AudioFileClip(audio_file_path)
    audio_clip = audio_normalize(audio_clip)
    audio = CompositeAudioClip([audio_clip])

    # Combine all visuals
    video = CompositeVideoClip(visual_clips, size=TARGET_SIZE)
    video.audio = audio
    video.duration = audio.duration

    # Write output video
    video.write_videofile(OUTPUT_FILE_NAME, codec='libx264', audio_codec='aac', fps=25, preset='veryfast')

    # Cleanup downloaded video files
    for temp_path in temp_video_paths:
        try:
            os.remove(temp_path)
        except Exception as e:
            print(f"Failed to delete temp file: {temp_path}, error: {e}")

    return OUTPUT_FILE_NAME

