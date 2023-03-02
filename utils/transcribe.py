import logging

import whisper


logger = logging.getLogger("VO-Transcriber")


def transcribe_file(input_file, language=None, model_name="small", verbose=False):
    model = whisper.load_model(model_name)

    options = {
        "fp16": False,
        "language": language,
    }

    result = model.transcribe(audio=input_file, verbose=verbose, **options)
    return result["segments"]
