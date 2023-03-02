# VO-Transcriber

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]

## A transcriber for VOs (Vorlesungen / Lectures) for Students of TU Wien and Uni Wien

This is a transcriber that uses Whisper (by OpenAI) to transcribe recorded lectures from the TU Wien and Uni Wien. It is a docker container that can be run on any machine that supports docker and has it installed.

I noticed that some of the lectures at TU Wien and Uni Wien are have poor or even no scripts available. This is a problem for students that want to learn from the lectures but don't have the time to watch them. This project aims to help solve this problem by providing transcripts for the lectures. Of course, this is not a perfect solution, but used in combination with some new AI-Tools like ChatGPT or the Bing Chat Bot, it can help students to learn from the lectures.

## Installation

> **Note:** You need to have docker installed on your machine. If you don't have docker installed, you can find the installation instructions [here][docker-install-url].

I do not recommend to install this project on your own machine and rather put this project onto a server. The reason for this is that the transriber uses a lot of resources and even only one transcription could take many hours to complete. If you want to use your own machine, you can but you are warned.

1. First of all you need to clone this repository to your local machine:

    ```bash
    git clone git@github.com:bananensplit/VO-Transcriber.git
    cd VO-Transcriber
    ```

2. Before you build the image please check in the `Dockerfile` if the correct lines are commented out. Depending on your architecture you need to uncomment the correct lines.

    ```Dockerfile
    # This is for ARM64
    RUN wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.buster_arm64.deb && \
    	apt install -y ./wkhtmltox_0.12.6-1.buster_arm64.deb && \
    	apt install -y openssl build-essential libssl-dev libxrender-dev git-core libx11-dev libxext-dev libfontconfig1-dev libfreetype6-dev fontconfig

    # This is for AMD64
    # RUN wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.buster_amd64.deb && \
    #     apt install -y ./wkhtmltox_0.12.6-1.buster_amd64.deb && \
    #     apt install -y openssl build-essential libssl-dev libxrender-dev git-core libx11-dev libxext-dev libfontconfig1-dev libfreetype6-dev fontconfig
    ```

    To check which architecture you have, you can run the following command

    ```powershell
    uname -m  # on Linux
    $Env:PROCESSOR_ARCHITECTURE # on Windows
    ```

3. Then you can build the image:

    ```bash
    docker build -t vo-transcriber:0.1.0 .
    ```

## Usage

The following section(s) contain(s) information on how to run the container and how to set the correct parameters.

### Parameters

-   `--help` - If this parameter is set, the help will be printed.
-   `--uni` - The university you want to transcribe the VOs from. Possible values are `tu` and `uw`.
-   `--vos` - The name of the VO you want to transcribe. This parameter can be used multiple times. If you don't provide this parameter, nothing will be transcribed.
-   `-p` - The path to the file containing the VO-data. Can be used with the `--uni` parameter set to `tu` or `uw`
-   `-k` - The link to the VO-data. Can be used with the `--uni` parameter set to `uw`.

    > usually the link to the data looks something like this: `https://ustream.univie.ac.at/search/episode.json?limit=200&offset=0&sid=XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX`

-   `-m` - The name of the [Whisper][whisper-url] model you want to use for transcribing. Possible values can be looked up on the [Whsiper Github][whisper-github-models-url].
-   `-v` - If this parameter is set, the verbose parameter will be passed to whisper and you will be able to see realtime translations.
-   `-l` - The language of the VO. Possible languages are listed [here][whisper-github-models-url]. Default is `de`.
-   `--txt` - If this parameter is set, the transcription will be saved as a `txt` file.
-   `--vtt` - If this parameter is set, the transcription will be saved as a `vtt` file (format for subtitles).
-   `--srt` - If this parameter is set, the transcription will be saved as a `srt` file (format for subtitles).
-   `--pdf` - If this parameter is set, the transcription will be saved as a `pdf` file.
-   `-o` - The output folder. Must be `output` (Docker and stuff).

### Startup - VO-Data from link

> **Note:** This only works for the Uni Wien. The TU-Wien (unlike the Uni Wien) has authentication which complicates things a bit. You can't provide a link to the data because this project doesn't support authentication (yet).

Before you start make sure the link you provide is correct and **public** (no login is required to retrieve the data).

1. To look up which vos are available, run the following command:

    ```bash
    docker run --rm --name vo-transcribe \
    	vo-transcriber:0.1.0 \
    	--uni "uw" \
    	-k "https://ustream.univie.ac.at/search/episode.json?limit=200&offset=0&sid=XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"
    ```

2. When you choose which VOs you want to transcribe, run the following command:

    ```bash
    mkdir output

    docker run -d --name vo-transcribe \
    	-v $(pwd)/output:/usr/src/app/output \
    	vo-transcriber:0.1.0 \
    	--uni "uw" \
    	-k "https://ustream.univie.ac.at/search/episode.json?limit=200&offset=0&sid=XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"
    	--vos "<name of the VO you want to transcribe>" \
    	--vos "<second VO you want to transcribe>" \
    	--vos "<... VO you want to transcribe>" \
    	--vos "<last VO you want to transcribe>" \
    	-o "output" \
    	-m "medium" \
    	-l "de" \
    	--txt \
    	--vtt \
    	--srt \
    	--pdf
    ```

You can of course adjust the parameters to your needs. This command would

-   transcribe 4 VOs
-   use the `medium` model (takes about 3 hours for 1,5 hours of VO)
-   use the `de` language
-   save the transcription as `txt`, `vtt`, `srt` and `pdf` files

### Startup - VO-Data from file

> **Note:** In the following instructions the `--uni` parameter is set to `tu` (TU Wien) but the same steps would also work for Uni Wien (`uw`).

1. Create the mount folder and the data file which contains the VO-data.

    ```bash
    mkdir ouput
    echo "data" > output/data.json
    ```

2. To look up which vos are available, run the following command:

    ```bash
    docker run --rm --name vo-transcribe \
    	-v $(pwd)/output:/usr/src/app/output \
    	vo-transcriber:0.1.0 \
    	--uni "tu" \
    	-p "output/data.json"
    ```

3. When you choose which VOs you want to transcribe, run the following command:

    ```bash
    docker run -d --name vo-transcribe \
    	-v $(pwd)/output:/usr/src/app/output \
    	vo-transcriber:0.1.0 \
    	--uni "tu" \
    	-p "output/data.json" \
    	--vos "<name of the VO you want to transcribe>" \
    	--vos "<second VO you want to transcribe>" \
    	--vos "<... VO you want to transcribe>" \
    	--vos "<last VO you want to transcribe>" \
    	-o "output" \
    	-m "medium" \
    	-l "de" \
    	--txt \
    	--vtt \
    	--srt \
    	--pdf
    ```

You can of course adjust the parameters to your needs. This command would

-   transcribe 4 VOs
-   use the `medium` model (takes about 3 hours for 1,5 hours of VO)
-   use the `de` language
-   save the transcription as `txt`, `vtt`, `srt` and `pdf` files

## Setup for development

This are instructions for people who might want to contribute to this project on how to get this project running on their local machine:

> **Note:** This project uses [Python 3.10][python-url] and i recommend to use [virtualenv][virtualenv-url] to manage all the dependencies.

### Setup

```bash
# Clone this repository
git clone git@github.com:bananensplit/VO-Transcriber.git
cd VO-Transcriber

# Create a virtual environment
python -m virtualenv venv
source venv/bin/activate

# Install the dependencies
pip install -r requirements.txt
```

### Run the project

This is as far as the setup goes. You can now run the project with the following command:

```bash
python main.py
# The main.py takes the same parameters as the docker image
# When no parameters are provided, the program will return its help message
```

### Build the docker image

To build the docker image, run the following command:

```bash
docker build -t vo-transcriber:0.1.0 .
```

## Find a bug? Have an idea?

If you find a bug in the source code or a mistake in the documentation, you can help me by submitting an issue in the [Issuetracker][issues-url]. Even better you can submit a Pull Request with a fix.

Furthermore if you have an idea for a new feature, feel free to submit an issue with a proposal for your new feature. Please add as much detail as possible to the issue description. This will help me to understand your idea and to discuss it with you.

**Thanks for making this project better!**

## Contact

Jeremiasz Zrolka - jeremiasz.zrolka@gmail.com

-   Twitter: [@jeremiasz_z][twitter-url]
-   Instagram: [@jeremiasz_z][instagram-url]
-   LinkedIn: [jeremiasz-zrolka][linkedin-url]

<!-- MARKDOWN LINKS & IMAGES -->

[repo]: https://github.com/bananensplit/VO-Transcriber
[contributors-shield]: https://img.shields.io/github/contributors/bananensplit/VO-Transcriber.svg
[contributors-url]: https://github.com/bananensplit/VO-Transcriber/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/bananensplit/VO-Transcriber.svg
[forks-url]: https://github.com/bananensplit/VO-Transcriber/network/members
[stars-shield]: https://img.shields.io/github/stars/bananensplit/VO-Transcriber.svg
[stars-url]: https://github.com/bananensplit/VO-Transcriber/stargazers
[issues-shield]: https://img.shields.io/github/issues/bananensplit/VO-Transcriber.svg
[issues-url]: https://github.com/bananensplit/VO-Transcriber/issues
[license-shield]: https://img.shields.io/github/license/bananensplit/VO-Transcriber.svg
[license-url]: https://github.com/bananensplit/VO-Transcriber/blob/master/LICENSE.md
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?logo=linkedin&colorB=555
[linkedin-url]: https://www.linkedin.com/in/jeremiasz-zrolka-78431021b
[twitter-url]: https://twitter.com/jeremiasz_z
[instagram-url]: https://instagram.com/jeremiasz_z
[docker-install-url]: https://docs.docker.com/get-docker/
[python-url]: https://www.python.org/downloads/release/python-3100/
[virtualenv-url]: https://virtualenv.pypa.io/en/latest/installation.html
[whisper-url]: https://openai.com/research/whisper
[whisper-github-url]: https://github.com/openai/whisper
[whisper-github-models-url]: https://github.com/openai/whisper#available-models-and-languages
