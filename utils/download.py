import logging

import youtube_dl as ydl


logger = logging.getLogger("VOs-Transcribe")


def download_only_audio(url, save_path):
    """
    Downloads the audio/video from the given url and converts it to MP3.
    :param url:         The url to download the audio/video from
    :param save_path:   The path to save the audio/video to (will be MP3 file)
    """
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": save_path,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
            }
        ],
    }
    with ydl.YoutubeDL(ydl_opts) as downlaod:
        downlaod.download([url])


def download(url, save_path):
    """
    Downloads the audio/video from the given url.
    :param url:         The url to download the audio/video from
    :param save_path:   The path to save the audio/video to (will be MP3 file)
    """
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": save_path,
    }
    with ydl.YoutubeDL(ydl_opts) as downlaod:
        downlaod.download([url])
