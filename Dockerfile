FROM python:3.10-buster

WORKDIR /usr/src/app

COPY requirements.txt ./
COPY main.py ./
COPY utils ./utils
COPY templates ./templates
COPY models ./models

RUN apt update && \
    apt install ffmpeg -y && \
    pip install --no-cache-dir -r requirements.txt && \
    mkdir output


# This is for ARM64
RUN wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.buster_arm64.deb && \
    apt install -y ./wkhtmltox_0.12.6-1.buster_amd64.deb && \
    apt install -y openssl build-essential libssl-dev libxrender-dev git-core libx11-dev libxext-dev libfontconfig1-dev libfreetype6-dev fontconfig

# This is for AMD64
# RUN wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.buster_amd64.deb && \
#     apt install -y ./wkhtmltox_0.12.6-1.buster_amd64.deb && \
#     apt install -y openssl build-essential libssl-dev libxrender-dev git-core libx11-dev libxext-dev libfontconfig1-dev libfreetype6-dev fontconfig


VOLUME /usr/src/app/output

ENTRYPOINT ["python", "main.py"]
CMD ["--help"]