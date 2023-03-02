FROM python:3.10

WORKDIR /usr/src/app

COPY requirements.txt ./
COPY main.py ./
COPY downloadVo.py ./
COPY convertToPDF.py ./
COPY transcribe.py ./
COPY templates/ ./templates

RUN apt update && \
    apt install ffmpeg -y && \
    apt install wkhtmltopdf -y && \
    pip install --no-cache-dir -r requirements.txt && \
    mkdir output

VOLUME /usr/src/app/output

ENTRYPOINT ["python", "main.py"]
CMD ["--help"]