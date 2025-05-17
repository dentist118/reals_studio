# Updated render_engine.py

def get_output_media(audio_file_path, timed_captions, background_video_data, video_server):
    OUTPUT_FILE_NAME = "rendered_video.mp4"
    magick_path = get_program_path("magick")
    os.environ['IMAGEMAGICK_BINARY'] = magick_path if magick_path else '/usr/bin/convert'

    # Extended video processing
    visual_clips = []
    audio_clips = [AudioFileClip(audio_file_path)]
    total_duration = audio_clips[0].duration

    # Process background videos with looping
    for (t1, t2), video_url in background_video_data:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            download_file(video_url, temp_file.name)
            video_clip = VideoFileClip(temp_file.name)
            
            # Loop video if segment duration longer than clip duration
            segment_duration = t2 - t1
            if video_clip.duration < segment_duration:
                loop_count = int(segment_duration / video_clip.duration) + 1
                video_clip = video_clip.loop(duration=segment_duration)
            
            video_clip = (video_clip
                         .subclip(0, segment_duration)
                         .set_start(t1)
                         .set_position('center'))
            visual_clips.append(video_clip)

    # Process captions with dynamic positioning
    for (start, end), text in timed_captions:
        text_clip = (TextClip(text, fontsize=100, color='white', 
                        stroke_color='black', stroke_width=3,
                        method='caption', size=(1000, None))
        text_clip = (text_clip.set_start(start)
                     .set_duration(end - start)
                     .set_position(('center', 0.8), relative=True))
        visual_clips.append(text_clip)

    # Create composite video with duration matching audio
    video = CompositeVideoClip(visual_clips, size=(1080, 1920))  # Vertical format
    video = video.set_duration(total_duration)
    video = video.set_audio(CompositeAudioClip(audio_clips))

    # Enhanced rendering parameters for longer videos
    video.write_videofile(
        OUTPUT_FILE_NAME,
        codec='libx264',
        audio_codec='aac',
        fps=30,
        preset='medium',
        ffmpeg_params=[
            '-crf', '23',
            '-movflags', '+faststart',
            '-threads', '4'
        ]
    )

    # Cleanup
    for clip in visual_clips:
        if isinstance(clip, VideoFileClip):
            clip.close()
            
    return OUTPUT_FILE_NAME
