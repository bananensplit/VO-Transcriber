import logging
from datetime import timedelta


logger = logging.getLogger("VOs-Transcribe")


def generate_txt(segments, output_file=None):
    logger.debug("Generating TXT")
    out = "\n".join(segment["text"].strip() for segment in segments)

    if output_file:
        with open(output_file, "w", encoding="UTF-8") as f:
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
        with open(output_file, "w", encoding="UTF-8") as f:
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
        with open(output_file, "w", encoding="UTF-8") as f:
            f.write(result)
            logger.info("Generated output VTT %s", output_file)

    logger.debug("Finished generating VTT")
    return result
