import os
import tempfile
import platform
import subprocess
from moviepy.editor import (
    AudioFileClip, 
    CompositeVideoClip, 
    VideoFileClip, 
    TextClip
)
from moviepy.config import change_settings
import requests

# Set ImageMagick path if needed
def get_program_path(program_name):
    try:
        search_cmd = "where" if platform.system() == "Windows" else "which"
        return subprocess.check_output([search_cmd, program_name]).decode().strip()
    except subprocess.CalledProcessError:
        return None

def download_file(url, filename):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    response = requests.get(url, headers=headers)
    with open(filename, 'wb') as f:
        f.write(response.content)

def get_output_media(audio_file_path, timed_captions, background_video_data, video_server):
    OUTPUT_FILE_NAME = "rendered_short.mp4"
    VIDEO_SIZE = (1080, 1920)  # Vertical Short format
    
    # Configure ImageMagick
    magick_path = get_program_path("magick")
    if magick_path:
        change_settings({"IMAGEMAGICK_BINARY": magick_path})

    # Load audio and get duration
    audio_clip = AudioFileClip(audio_file_path)
    total_duration = audio_clip.duration

    # Process background videos
    visual_clips = []
    for (t1, t2), video_url in background_video_data:
        if video_url:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
                download_file(video_url, temp_file.name)
                video_clip = VideoFileClip(temp_file.name)
                
                # Resize and loop video if needed
                video_clip = video_clip.resize(VIDEO_SIZE)
                segment_duration = t2 - t1
                if video_clip.duration < segment_duration:
                    video_clip = video_clip.loop(duration=segment_duration)
                
                video_clip = (
                    video_clip.subclip(0, segment_duration)
                    .set_start(t1)
                    .set_position("center")
                )
                visual_clips.append(video_clip)

    # Process captions (yellow text without stroke)
    for (start, end), text in timed_captions:
        text_clip = TextClip(
            txt=text,
            fontsize=120,
            color="yellow",
            method="caption",
            align="center",
            size=(1000, None),  # Width constraint for vertical
            font="Arial-Bold"
        )
        text_clip = (
            text_clip.set_start(start)
            .set_duration(end - start)
            .set_position(("center", 0.75), relative=True)
        )
        visual_clips.append(text_clip)

    # Create final composition
    video = CompositeVideoClip(
        visual_clips,
        size=VIDEO_SIZE
    ).set_duration(total_duration)

    # Add audio
    video = video.set_audio(audio_clip)

    # Render with optimized settings
    video.write_videofile(
        OUTPUT_FILE_NAME,
        codec="libx264",
        audio_codec="aac",
        fps=30,
        preset="fast",
        ffmpeg_params=[
            "-crf", "23",
            "-movflags", "+faststart"
        ]
    )

    # Cleanup
    for clip in visual_clips:
        if isinstance(clip, VideoFileClip):
            clip.close()
    
    return OUTPUT_FILE_NAME
