import os
import requests
from utility.utils import log_response, LOG_TYPE_PEXEL

PEXELS_API_KEY = os.environ.get('PEXELS_KEY')

def search_videos(query_string, orientation_landscape=True):
    url = "https://api.pexels.com/videos/search"
    headers = {
        "Authorization": PEXELS_API_KEY,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    params = {
        "query": query_string,
        "orientation": "landscape" if orientation_landscape else "portrait",
        "per_page": 15
    }

    response = requests.get(url, headers=headers, params=params)
    json_data = response.json()
    log_response(LOG_TYPE_PEXEL, query_string, json_data)
    return json_data

def getBestVideo(query_string, orientation_landscape=True, used_vids=[]):
    vids = search_videos(query_string, orientation_landscape)
    videos = vids['videos']

    def is_aspect_ratio(w, h, target_ratio=16/9, tolerance=0.05):
        return abs((h / w) - target_ratio) < tolerance

    if orientation_landscape:
        filtered_videos = [
            video for video in videos
            if video['width'] >= 1920 and video['height'] >= 1080 and is_aspect_ratio(video['width'], video['height'])
        ]
    else:
        filtered_videos = [
            video for video in videos
            if video['width'] >= 1080 and video['height'] >= 1920 and is_aspect_ratio(video['width'], video['height'])
        ]

    sorted_videos = sorted(filtered_videos, key=lambda x: abs(15 - int(x['duration'])))

    for video in sorted_videos:
        for video_file in video['video_files']:
            if orientation_landscape:
                if video_file['width'] == 1920 and video_file['height'] == 1080:
                    if not (video_file['link'].split('.hd')[0] in used_vids):
                        return video_file['link']
            else:
                if video_file['width'] == 1080 and video_file['height'] == 1920:
                    if not (video_file['link'].split('.hd')[0] in used_vids):
                        return video_file['link']

    print("NO LINKS found for this round of search with query:", query_string)
    return None

def generate_video_url(timed_video_searches, video_server, orientation_landscape=False):
    timed_video_urls = []
    if video_server == "pexel":
        used_links = []
        for (t1, t2), search_terms in timed_video_searches:
            url = ""
            for query in search_terms:
                url = getBestVideo(query, orientation_landscape=orientation_landscape, used_vids=used_links)
                if url:
                    used_links.append(url.split('.hd')[0])
                    break
            timed_video_urls.append([[t1, t2], url])
    elif video_server == "stable_diffusion":
        timed_video_urls = get_images_for_video(timed_video_searches)

    return timed_video_urls
