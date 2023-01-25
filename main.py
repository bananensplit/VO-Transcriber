import argparse
import logging
import os
from datetime import datetime

from convertToPDF import convert_to_PDF_vo_data
from downloadVo import download_only_audio, get_all_vo_data
from transcribe import generate_srt, generate_txt, generate_vtt, transcribe_file


def download_vo(vo_data: str, output_file: str):
    """
    Downloads the audio track of the given vo_data to the given output_file
    :param vo_data:         The vo_data to download
    :param output_file:     The output file to save the audio track to
    """
    logger.info("Downloading " + vo_data["mediapackage"]["title"])
    tracks = vo_data["mediapackage"]["media"]["track"]
    audio_tracks = [track for track in tracks if track["mimetype"].startswith("audio")]

    if len(audio_tracks) == 0:
        url = tracks[0]["url"]
        logger.warning(
            "No audio track found for '%s' found!\nDownloading whole video and extracting audio track (will take more time)",
            vo_data["mediapackage"]["title"],
        )
        logger.debug("Downloading video for '%s' from '%s'", vo_data["mediapackage"]["title"], url)
        download_only_audio(url, output_file)
        logger.info("Downloaded audio track for '%s' to '%s'", vo_data["mediapackage"]["title"], output_file)
    else:
        url = audio_tracks[0]["url"]
        logger.info("Found audiotrack for '%s'", vo_data["mediapackage"]["title"])
        logger.debug("Downloading audio track for '%s' from '%s'", vo_data["mediapackage"]["title"], url)
        download_only_audio(url, output_file)
        logger.info("Downloaded audio track for '%s' to '%s'", vo_data["mediapackage"]["title"], output_file)


def generate_transcribtions_vo(
    audio_path: str,
    vo_data: str,
    output_folder: str,
    language: str = None,
    model_name: str = "tiny",
    verbose: bool = False,
    txt: bool = True,
    vtt: bool = False,
    srt: bool = False,
    pdf: bool = False,
):
    """
    Transcribes the audio file at the given path and generates the output files.
    :param audio_path:      Path to the audio file to transcribe
    :param vo_data:         The vo data
    :param output_folder:   The folder to save the output files to
    :param language:        Language of the given audio file
    :param model_name:      Name of the whisper-model to use for transcription
    :param verbose:         Whether to print the transcription to the console (will print each segment after it is transcribed)
    :param txt:             Whether to generate a txt file
    :param vtt:             Whether to generate a vtt file
    :param srt:             Whether to generate a srt file
    :param pdf:             Whether to generate a pdf file
    """
    logger.info("Transcribing '%s'", audio_path)
    segments = transcribe_file(
        input_file=audio_path,
        language=language,
        model_name=model_name,
        verbose=verbose,
    )

    if txt:
        generate_txt(segments, os.path.join(output_folder, vo_data["mediapackage"]["title"] + ".txt"))
    if vtt:
        generate_vtt(segments, os.path.join(output_folder, vo_data["mediapackage"]["title"] + ".vtt"))
    if srt:
        generate_srt(segments, os.path.join(output_folder, vo_data["mediapackage"]["title"] + ".srt"))
    if pdf:
        vo_data = {
            "vo_titel": vo_data["mediapackage"]["title"],
            "autor": vo_data["mediapackage"]["creators"]["creator"],
            "beitragende": vo_data["mediapackage"]["contributors"]["contributor"],
            "length": str(datetime.timedelta(milliseconds=vo_data["mediapackage"]["duration"])),
            "recorded_on": datetime.strptime(vo_data["mediapackage"]["start"], "%Y-%m-%dT%H:%M:%SZ"),
            "series_name": vo_data["mediapackage"]["seriestitle"],
            "link": vo_data["mediapackage"]["media"]["track"][0]["url"],
        }
        path = os.path.join(output_folder, vo_data["mediapackage"]["title"] + ".pdf")
        transcription = generate_txt(segments)
        convert_to_PDF_vo_data(
            output_path=path,
            vo_titel=vo_data["mediapackage"]["vo_titel"],
            autor=vo_data["mediapackage"]["creators"]["creator"],
            beitragende=vo_data["mediapackage"]["contributors"]["contributor"],
            length=vo_data["mediapackage"]["length"],
            recorded_on=vo_data["mediapackage"]["start"],
            series_name=vo_data["mediapackage"]["seriestitle"],
            link=vo_data["mediapackage"]["media"]["track"][0]["url"],
            transcription=transcription,
        )
    logger.info("Finished transcribing '%s'", audio_path)


def main(args):
    all_vo_data = get_all_vo_data(args.data_path, args.data_link)
    logger.debug("All Vos found: \n%s", "\n".join([20 * " " + vo["mediapackage"]["title"] for vo in all_vo_data]))

    if args.vos is None or len(args.vos) == 0:
        logger.error("No VOs to transcribe given! Exiting")
        return

    vos_to_transcribe = [vo for vo in all_vo_data if vo["mediapackage"]["title"] in args.vos]
    logger.info("VOs to be transcribed: \n%s", "\n".join([20 * " " + vo["mediapackage"]["title"] for vo in vos_to_transcribe]))

    # Download VOs
    logger.info("Downloading VOs")
    audios_output_folder = os.path.join(args.output_folder, "audios")
    logger.debug("Creating output folder for VO-audios: '%s'", audios_output_folder)

    if not os.path.isdir(audios_output_folder):
        os.mkdir(audios_output_folder)

    paths_to_audios = [os.path.join(audios_output_folder, vo["mediapackage"]["title"] + ".mp3") for vo in vos_to_transcribe]
    for vo_data, path in zip(vos_to_transcribe, paths_to_audios):
        start = datetime.now()
        download_vo(vo_data, path)
        end = datetime.now()
        logger.info("Downloading took %s", str(end - start))

    logger.info("Finished downloading VOs")

    # Transcribe VOs
    logger.info("Transcribing VOs")
    logger.debug("Creating output folder for VO-transcriptions")
    transcription_output_folder = os.path.join(args.output_folder, "transcriptions")
    logger.debug("Creating output folder for VO-transcriptions: '%s'", transcription_output_folder)

    if not os.path.isdir(transcription_output_folder):
        os.mkdir(transcription_output_folder)

    for vo_data, audio_path in zip(all_vo_data, paths_to_audios):
        start = datetime.now()
        generate_transcribtions_vo(
            audio_path=audio_path,
            output_folder=transcription_output_folder,
            vo_data=vo_data,
            language=args.language,
            model_name=args.model_name,
            verbose=args.verbose,
            txt=args.txt,
            vtt=args.vtt,
            srt=args.srt,
            pdf=args.pdf,
        )
        end = datetime.now()
        logger.info("Transcribing took %s", str(end - start))

    logger.info("Finished transcribing VOs")


if __name__ == "__main__":
    # Setup argparse
    parser = argparse.ArgumentParser(description="Transcribe audio files to text")

    # Download data
    vo_data_links = parser.add_mutually_exclusive_group()
    vo_data_links.add_argument("--data-path", "-p", type=str, default=None, help="path to the file where the VO-data is stored, this path is not influenced by the -i/--input-folder argument")
    vo_data_links.add_argument("--data-link", "-k", type=str, default=None, help="link to the VO-Data of u:space")
    parser.add_argument("--vos", action="append", type=str, help="Titels of the VOs which shall be transcribed. If this argument is not set, no VOs will be transcribed.")

    # Transcribe options
    parser.add_argument("--model-name", "-m", type=str, default="tiny", help="which whisper model shall be used for transcribing")
    parser.add_argument("--language", "-l", type=str, default="None", help="language which shall be used for transcribing")
    parser.add_argument("--verbose", "-v", action="store_true", help="does print the ouput of the transcribtion to the console")
    parser.add_argument("--txt", action="store_true", help="if set the audios will be transcibed to txt")
    parser.add_argument("--vtt", action="store_true", help="if set the audios will be transcibed to vtt")
    parser.add_argument("--srt", action="store_true", help="if set the audios will be transcibed to srt")

    # PDF options
    parser.add_argument("--pdf", action="store_true", help="if set the audios will be transcibed to pdf")
    parser.add_argument("--page-numbers", "-n", action="store_true", help="if set page numbers will be added to the pdfs (-pdf has to be set)")
    # parser.add_argument("--add-info", "-i", action="store_true", help="if set the pdfs will contain information about the VOs (-pdf has to be set)")

    # Output options
    parser.add_argument("-o", "--output_folder", default="output", help="outputfolder where every ouput (audios and transcriptions) shall be stored")

    # args = parser.parse_args(["--help"])
    # args = parser.parse_args(
        # ["-p", "data.json", "-vos", "2. Aufzeichnung vom 20.12.2022", "-o", "output", "-m", "tiny", "-l", "de", "-v", "--pdf", "--page-numbers"]
    # )
    args = parser.parse_args()

    if not os.path.isdir(args.output_folder):
        parser.error("Output folder does not exist: " + args.output_folder)

    # Setup logging
    logger = logging.getLogger("VOs-Transcribe")
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(os.path.join(args.output_folder, "VOs-Transcribe.log"))
    ch = logging.StreamHandler()
    formatter = logging.Formatter(fmt="%(asctime)s %(levelname)-8s %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)

    logger.warning("Starting script")
    main(args)
    logger.warning("Finished script")
