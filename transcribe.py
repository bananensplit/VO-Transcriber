import argparse
import logging
import os
from datetime import datetime, timedelta
from glob import glob

import whisper


def transcribe_file(input_file, output_folder, language=None, model_name="small", verbose=False):
    model = whisper.load_model(model_name)

    options = {
        "fp16": False,
        "language": language,
    }

    result = model.transcribe(audio=input_file, verbose=verbose, **options)

    output_file_txt = os.path.join(output_folder, os.path.basename(input_file) + ".txt")
    output_file_srt = os.path.join(output_folder, os.path.basename(input_file) + ".srt")
    output_file_vtt = os.path.join(output_folder, os.path.basename(input_file) + ".vtt")

    # TXT
    with open(output_file_txt, 'w') as f:
        out = "\n".join(segment["text"].strip() for segment in result["segments"])
        f.write(out)
    logger.info("Generated output TXT" + output_file_txt)

    # SRT
    with open(output_file_srt, 'w') as f:
        out = []
        for index, segment in enumerate(result["segments"], start=1):
            start = timedelta(seconds=int(segment["start"]))
            end = timedelta(seconds=int(segment["end"]))
            out.append(f"{index}\n{start},000 --> {end},000\n{segment['text'].strip()}")
        f.write("\n\n".join(out))
    logger.info("Generated output SRT" + output_file_srt)

    # VTT
    with open(output_file_vtt, 'w') as f:
        out = []
        for segment in result["segments"]:
            start = timedelta(seconds=int(segment["start"]))
            end = timedelta(seconds=int(segment["end"]))
            out.append(f"{start},000 --> {end},000\n{segment['text'].strip()}")
        f.write("\n\n".join(out))
    logger.info("Generated output VTT" + output_file_vtt)
    

def transcribe_all(audio_files, output_folder, language=None, model_name="small", verbose=False):
    for audio_file in audio_files:
        start = datetime.now()
        logger.info("Transcribing " + audio_file)
        transcribe_file(input_file=audio_file, output_folder=output_folder, language=language, model_name=model_name, verbose=verbose)
        logger.info("Finished transcribing " + audio_file)
        end = datetime.now()
        logger.info("Transcribing took " + str(end - start))


if __name__ == '__main__':
    # Setup Argparse
    parser = argparse.ArgumentParser(description='Transcribe audio files to text')

    parser.add_argument('-m', '--model_name', default='tiny', help='which whisper model shall be used for transcribing')
    parser.add_argument('-l', '--language', default='None', help='language which shall be used for transcribing')
    parser.add_argument('-v', '--verbose', action='store_true', help='does the ouput of the transcribtion to the console')
    parser.add_argument('-i', '--input_folder', default='input', help='inputfolder all audio_files paths are relative to this path')
    parser.add_argument('-o', '--output_folder', default='output', help='outputfolder where the transcribtions will be stored')
    parser.add_argument('audio_files', nargs='+', help='one or more audiofiles that shall be transcribed (supports only mp3)')

    # args = parser.parse_args(["--help"])
    args = parser.parse_args()

    if not os.path.isdir(args.input_folder):
        parser.error("Input folder does not exist: " + args.input_folder)
    if not os.path.isdir(args.output_folder):
        parser.error("Output folder does not exist: " + args.output_folder)
    
    # Setup logging
    logger = logging.getLogger("VO-Transcribe")
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(os.path.join(args.output_folder, 'VO-Transcribe.log'))
    ch = logging.StreamHandler()
    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)

    logger.warning("Starting script")
    logger.info("Input folder:  " + args.input_folder)
    logger.info("Output folder: " + args.output_folder)
    logger.info("Audio files:   " + str(args.audio_files))

    # Get all files
    files = set()
    for path in args.audio_files:
        path = os.path.join(args.input_folder, path)
        for file in glob(path):
            if os.path.isfile(file):
                files.add(file)

    logger.info("Files: " + ", ".join(files))

    # Get correct language
    if args.language.strip() == "None":
        args.language = None

    # Transcribe
    transcribe_all(files, args.output_folder, args.language, args.model_name, args.verbose)

    logger.warning("Finished script")
