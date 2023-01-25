import logging
import os
from datetime import datetime, timedelta

import whisper

logger = logging.getLogger("VOs-Transcribe")


def transcribe_file(input_file, language=None, model_name="small", verbose=False):
    model = whisper.load_model(model_name)

    options = {
        "fp16": False,
        "language": language,
    }

    result = model.transcribe(audio=input_file, verbose=verbose, **options)
    return result["segments"]


def generate_txt(segments, output_file=None):
    logger.debug("Generating TXT")
    out = "\n".join(segment["text"].strip() for segment in segments)

    if output_file:
        with open(output_file, 'w') as f:
            f.write(out)
            logger.info("Generated output TXT %s" + output_file)

    logger.debug("Finished generating TXT")
    return out


def generate_srt(segments, output_file=None):
    logger.debug("Generating SRT")
    out = []
    for index, segment in enumerate(segments, start=1):
        start = timedelta(seconds=int(segment["start"]))
        end = timedelta(seconds=int(segment["end"]))
        out.append(f"{index}\n{start},000 --> {end},000\n{segment['text'].strip()}")

    result = "\n\n".join(out)
    if output_file:
        with open(output_file, 'w') as f:
            f.write(result)
            logger.info("Generated output SRT %s", output_file)

    logger.debug("Finished generating SRT")
    return result


def generate_vtt(segments, output_file=None):
    logger.debug("Generating VTT")
    out = []
    for segment in segments:
        start = timedelta(seconds=int(segment["start"]))
        end = timedelta(seconds=int(segment["end"]))
        out.append(f"{start},000 --> {end},000\n{segment['text'].strip()}")

    result = "\n\n".join(out)
    if output_file:
        with open(output_file, 'w') as f:
            f.write()
            logger.info("Generated output VTT %s", output_file)

    logger.debug("Finished generating VTT")
    return result


def transcribe_all(audio_files: list, output_folder, language=None, model_name="small", verbose=False):
    for audio_file in audio_files:
        start = datetime.now()
        logger.info("Transcribing " + audio_file)

        output_file_txt = os.path.join(output_folder, os.path.basename(audio_file) + ".txt")
        output_file_srt = os.path.join(output_folder, os.path.basename(audio_file) + ".srt")
        output_file_vtt = os.path.join(output_folder, os.path.basename(audio_file) + ".vtt")
        
        result = transcribe_file(input_file=audio_file, output_folder=output_folder, language=language, model_name=model_name, verbose=verbose)
        generate_txt(result, output_file_txt)
        generate_srt(result, output_file_srt)
        generate_vtt(result, output_file_vtt)
        
        logger.info("Finished transcribing " + audio_file)
        end = datetime.now()
        logger.info("Transcribing took " + str(end - start))
