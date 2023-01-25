FROM python:3.10

WORKDIR /usr/src/app

ENV ARGS=""

COPY requirements.txt ./
COPY main.py ./
COPY transcribe.py ./
COPY convertToPDF.py ./
COPY templates ./

RUN apt update
RUN apt install ffmpeg -y
RUN apt install wkhtmltopdf -y

RUN pip install --no-cache-dir -r requirements.txt
RUN mkdir input
RUN mkdir output

VOLUME /usr/src/app/output

# CMD ["python", "transcribe.py", "-v", "-m", "$WHISPER_MODEL", "-l", "$LANGUAGE", "$AUDIO_FILES"]
CMD python main.py $ARGS