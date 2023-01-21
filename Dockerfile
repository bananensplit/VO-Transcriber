FROM python:3.9

WORKDIR /usr/src/app

ENV AUDIO_FILES="*"
ENV LANGUAGE="None"
ENV WHISPER_MODEL="*"

COPY transcribe.py ./
COPY requirements.txt ./

RUN apt update && apt install ffmpeg -y

RUN pip install --no-cache-dir -r requirements.txt
RUN mkdir input
RUN mkdir output

VOLUME /usr/src/app/input
VOLUME /usr/src/app/output

# CMD ["python", "transcribe.py", "-v", "-m", "$WHISPER_MODEL", "-l", "$LANGUAGE", "$AUDIO_FILES"]
CMD python transcribe.py -v -m $WHISPER_MODEL -l $LANGUAGE "$AUDIO_FILES"