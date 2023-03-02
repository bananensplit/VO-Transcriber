import argparse
from datetime import datetime
import logging
import os

from models.VoDataModels import VoData
from utils.transcribe import transcribe_file
from utils.download import download_only_audio
from utils.generate_PDF import convert_to_PDF_vo_data
from utils.generate_files import generate_srt, generate_txt, generate_vtt
from utils.vo_data import get_all_vo_data, parse_vo_data_tu, parse_vo_data_uni_wien


def download_vo(vo_data: VoData, output_file: str):
    """
    Downloads the audio track of the given vo_data to the given output_file
    :param vo_data:         The vo_data to download
    :param output_file:     The output file to save the audio track to
    """
    logger.info("Downloading %s", vo_data.vo_title)

    if vo_data.vo_mp3_link is not None:
        logger.warning(
            "No audio track found for '%s' found!\nDownloading whole video and extracting audio track (will take more time)",
            vo_data.vo_title,
        )
        logger.debug("Downloading video for '%s' from '%s'", vo_data.vo_title, vo_data.vo_mp3_link)
        download_only_audio(vo_data.vo_mp3_link, output_file)
        logger.info("Downloaded video and extracted audio track for '%s' to '%s'", vo_data.vo_title, output_file)
    elif vo_data.vo_mp4_link is not None:
        logger.info("Found audiotrack for '%s'", vo_data.vo_title)
        logger.debug("Downloading audio track for '%s' from '%s'", vo_data.vo_title, vo_data.vo_mp4_link)
        download_only_audio(vo_data.vo_mp4_link, output_file)
        logger.info("Downloaded audio track for '%s' to '%s'", vo_data.vo_title, output_file)


def generate_transcribtions_vo(
    audio_path: str,
    vo_data: VoData,
    output_folder: str,
    language: str = None,
    model_name: str = "tiny",
    verbose: bool = False,
    txt: bool = True,
    vtt: bool = False,
    srt: bool = False,
    pdf: bool = False,
    pdf_page_numbers: bool = False,
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
        generate_txt(segments, os.path.join(output_folder, vo_data.vo_title + ".txt"))
    if vtt:
        generate_vtt(segments, os.path.join(output_folder, vo_data.vo_title + ".vtt"))
    if srt:
        generate_srt(segments, os.path.join(output_folder, vo_data.vo_title + ".srt"))
    if pdf:
        path = os.path.join(output_folder, vo_data.vo_title + ".pdf")
        transcription = generate_txt(segments)
        convert_to_PDF_vo_data(
            output_file=path,
            vo_title=vo_data.vo_title,
            autor=vo_data.author,
            beitragende=vo_data.contributors,
            length=vo_data.duration,
            recorded_on=vo_data.recorded_on,
            series_name=vo_data.series_title,
            link=vo_data.vo_mp4_link,
            transcription=transcription,
            page_numbers=pdf_page_numbers,
        )
    logger.info("Finished transcribing '%s'", audio_path)


def main(args):
    # Getting VO-Data
    all_vo_data = get_all_vo_data(args.data_path, args.data_link)
    if all_vo_data is None:
        logger.error("Could not get VO-Data! Exiting")
        return

    # Parseing VO-Data
    if args.uni == "uw":
        all_vo_data = parse_vo_data_uni_wien(all_vo_data)
    elif args.uni == "tu":
        all_vo_data = parse_vo_data_tu(all_vo_data)

    logger.debug("All Vos found: \n%s", "\n".join([20 * " " + vo.vo_title for vo in all_vo_data]))

    # Getting VOs to transcribe
    if args.vos is None or len(args.vos) == 0:
        logger.error("No VOs to transcribe given! Exiting")
        return

    vos_to_transcribe = [vo for vo in all_vo_data if vo.vo_title in args.vos]
    logger.info("VOs to be transcribed: \n%s", "\n".join([20 * " " + vo.vo_title for vo in vos_to_transcribe]))

    # Download VOs
    logger.info("Downloading VOs")
    audios_output_folder = os.path.join(args.output_folder, "audios")
    logger.debug("Creating output folder for VO-audios: '%s'", audios_output_folder)

    if not os.path.isdir(audios_output_folder):
        os.mkdir(audios_output_folder)

    paths_to_audios = [os.path.join(audios_output_folder, vo.vo_title + ".mp3") for vo in vos_to_transcribe]
    for vo_data, path in zip(vos_to_transcribe, paths_to_audios):
        start = datetime.now()
        download_vo(vo_data, path)
        end = datetime.now()
        logger.info("Downloading took %s", str(end - start))

    logger.info("Finished downloading VOs")

    # Transcribe VOs
    logger.info("Transcribing VOs")
    transcription_output_folder = os.path.join(args.output_folder, "transcriptions")
    logger.debug("Created output folder for VO-transcriptions: '%s'", transcription_output_folder)

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
            pdf=args.pdf or args.pdf_no_num,
            pdf_page_numbers=args.pdf,
        )
        end = datetime.now()
        logger.info("Transcribing took %s", str(end - start))

    logger.info("Finished transcribing VOs")


if __name__ == "__main__":
    # Setup argparse
    parser = argparse.ArgumentParser(description="Transcribe audio files to text")

    # Data format
    parser.add_argument("--uni", choices=["uw", "tu"], required=True, help="Which university is the data from")

    # Download data
    vo_data_links = parser.add_mutually_exclusive_group()
    vo_data_links.add_argument(
        "--data-path",
        "-p",
        type=str,
        default=None,
        help="path to the file where the VO-data is stored, this path is not influenced by the -i/--input-folder argument",
    )
    vo_data_links.add_argument("--data-link", "-k", type=str, default=None, help="link to the VO-Data of u:space")
    parser.add_argument(
        "--vos",
        action="append",
        type=str,
        help="Titels of the VOs which shall be transcribed. If this argument is not set, no VOs will be transcribed.",
    )

    # Transcribe options
    parser.add_argument("--model-name", "-m", type=str, default="tiny", help="which whisper model shall be used for transcribing")
    parser.add_argument(
        "--language",
        "-l",
        type=str,
        default="de",
        help="language which shall be used for transcribing (defaults to 'de' for german)",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="does print the ouput of the transcribtion to the console")
    parser.add_argument("--txt", action="store_true", help="if set the audios will be transcibed to txt")
    parser.add_argument("--vtt", action="store_true", help="if set the audios will be transcibed to vtt")
    parser.add_argument("--srt", action="store_true", help="if set the audios will be transcibed to srt")

    # PDF options
    pdf_options = parser.add_mutually_exclusive_group()
    pdf_options.add_argument("--pdf", action="store_true", help="if set the audios will be transcibed to pdfs with page numbers")
    pdf_options.add_argument(
        "--pdf-no-num", action="store_true", help="if set the audios will be transcibed to pdfs without page numbers"
    )

    # Output options
    parser.add_argument(
        "-o",
        "--output_folder",
        default="output",
        help="outputfolder where every ouput (audios and transcriptions) shall be stored",
    )

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
