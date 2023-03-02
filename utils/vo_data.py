import json
import logging
import os
from datetime import datetime, timedelta

import requests

from models.VoDataModels import VoData


logger = logging.getLogger("VOs-Transcribe")


def get_all_vo_data(path=None, link=None):
    """
    Loads the VO-Data from the given file or link. When file is given link is ignored.
    :param path:    Path to the file containing the VO-Data (is mutually exclusive with link)
    :param link:    Link to the file containing the VO-Data (is mutually exclusive with path)
    """
    if path is not None:
        logger.info("Trying to load VO-Data from file: %s", path)
        if not os.path.isfile(path):
            logger.error("VO-data file is not a file or doesn't exist: %s", path)
        try:
            with open(path, "r", encoding="UTF-8") as f:
                vo_data = json.load(f)
                return vo_data["search-results"]["result"]
        except Exception as e:
            logger.error("Could not load VO-data from file: %s", path)

    if link is not None:
        logger.info("Trying to load VO-data from link: %s", link)
        try:
            response = requests.get(link, timeout=5)
            vo_data = response.json()
            return vo_data["search-results"]["result"]
        except Exception as e:
            logger.error("Could not load VO-data from link: %s", link)

    logger.info("Could not load VO-data from file or link. Returning None.")
    return None


def parse_vo_data_tu(data) -> list[VoData]:
    """
    Parses the VO-Data from TU Wien.
    :param data:    The VO-Data to parse
    :return:        A list of VoData objects
    """
    erg = []

    for vo in data:
        vo_mp4_link = None
        if isinstance(vo["mediapackage"]["media"]["track"], list):
            mp4_tracks = [track for track in vo["mediapackage"]["media"]["track"] if track["mimetype"].startswith("video/mp4")]
            mp4_track_high_res = max(mp4_tracks, key=lambda x: int(x["video"]["resolution"].split("x", 1)[0]))
            vo_mp4_link = mp4_track_high_res["url"]
        else:
            vo_mp4_link = vo["mediapackage"]["media"]["track"]["url"]

        vo_mp3_link = None
        if isinstance(vo["mediapackage"]["media"]["track"], list):
            mp3_tracks = [track for track in vo["mediapackage"]["media"]["track"] if track["mimetype"].startswith("audio/mpeg")]
            mp3_track_high_res = max(mp3_tracks, key=lambda x: int(x["audio"]["bitrate"]))
            vo_mp3_link = mp3_track_high_res["url"]

        erg.append(VoData(
            vo_mp4_link=vo_mp4_link,
            vo_mp3_link=vo_mp3_link,
            vo_title=vo["mediapackage"]["title"],
            author=vo["mediapackage"]["creators"]["creator"],
            series_title=vo["mediapackage"]["seriestitle"],
            duration=timedelta(milliseconds=int(vo["mediapackage"]["duration"])),
            recorded_on=datetime.strptime(vo["dcCreated"], "%Y-%m-%dT%H:%M:%S%z")
        ))

    return erg

def parse_vo_data_uni_wien(data) -> list[VoData]:
    """
    Parses the VO-Data from Uni Wien.
    :param data:    The VO-Data to parse
    :return:        A list of VoData objects
    """
    erg = []

    for vo in data:
        mp4_tracks = [track for track in vo["mediapackage"]["media"]["track"] if track["mimetype"].startswith("video/mp4")]
        mp4_track_high_res = max(mp4_tracks, key=lambda x: int(x["tags"]["tag"][0][:9]))
        erg.append(VoData(
            vo_mp4_link=mp4_track_high_res["url"],
            vo_title=vo["mediapackage"]["title"],
            author=vo["mediapackage"]["creators"]["creator"],
            contributors=vo["mediapackage"]["contributors"]["contributor"],
            series_title=vo["mediapackage"]["seriestitle"],
            duration=timedelta(milliseconds=int(vo["mediapackage"]["duration"])),
            recorded_on=datetime.strptime(vo["dcCreated"], "%Y-%m-%dT%H:%M:%S%z")
        ))

    return erg