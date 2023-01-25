import json
import logging
import os

import requests
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


def get_all_vo_data(path=None, link=None):
    """
    Loads the VO-Data from the given file or link. When file is given link is ignored.
    :param path:    Path to the file containing the VO-Data (is mutually exclusive with link)
    :param link:    Link to the file containing the VO-Data (is mutually exclusive with path)
    """
    if path is not None:
        logger.info("Trying to load VO-Data from file: %s", path)
        if not os.path.isfile(path):
            logger.error("VO-data file is not a file or doesn't exist: ", path)

        try:
            with open(path, "r", encoding="UTF-8") as f:
                vo_data = json.load(f)
                return vo_data["search-results"]["result"]
        except Exception as e:
            logger.error("Could not load VO-data from file: %s", path)

    if link is not None:
        logger.info("Trying to load VO-data from link: %s", link)
        try:
            response = requests.get(link)
            vo_data = response.json()
            return vo_data["search-results"]["result"]
        except Exception as e:
            logger.error("Could not load VO-data from link: %s", link)

    logger.info("Could not load VO-data from file or link. Returning None.")
    return None
