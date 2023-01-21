import argparse
import json
import logging
import os
from datetime import datetime, timedelta

import jinja2
import pdfkit
import requests


def convert_to_PDF_vo_data(vo_data, transcription, output_file, page_numbers=False):
    logger.info("Generating PDF (with VO-Data) for " + vo_data["mediapackage"]["title"])
    logger.debug("  Outputfile:    " + output_file)
    logger.debug("  Page numbers:  " + str(page_numbers))
    # logger.debug("  VO-Data:       " + json.dumps(vo_data))
    # logger.debug("  Transcription: " + str(transcription))

    context = {
        "vo_titel":     vo_data["mediapackage"]["title"],
        "autor":        vo_data["mediapackage"]["creators"]["creator"],
        "beitragende":  vo_data["mediapackage"]["contributors"]["contributor"],
        "length":       str(timedelta(milliseconds=vo_data["mediapackage"]["duration"])),
        "recorded_on":  datetime.strptime(vo_data["mediapackage"]["start"], "%Y-%m-%dT%H:%M:%SZ").strftime("%d.%m.%Y %H:%M"),
        "series_name":  vo_data["mediapackage"]["seriestitle"],
        "link":         vo_data["mediapackage"]["media"]["track"][0]["url"],
        "transcription": transcription,
    }
    logger.debug("  Context:      " + str({k:v for (k, v) in context.items() if k != "transcription"}))

    template_loader = jinja2.FileSystemLoader(searchpath="./templates")
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template("vo_data_index.html")
    
    output_html = template.render(context)
    options = {
        "page-size": "A4",
        "margin-top": "15mm",
        "margin-right": "15mm",
        "margin-bottom": "15mm",
        "margin-left": "15mm",
    }
    if page_numbers: options["footer-right"] = "[page] / [topage]"
    logger.debug("  Options:       " + str(options))

    pdfkit.from_string(output_html, output_file, options=options)
    logger.info(f"Generated PDF for '{vo_data['mediapackage']['title']}' at '{output_file}'")


def convert_to_PDF(transcription, output_file, page_numbers=False):
    logger.info("Generating PDF for " + os.path.basename(output_file))
    logger.debug("  Outputfile:    " + output_file)
    logger.debug("  Page numbers:  " + str(page_numbers))
    # logger.debug("  Transcription: " + str(transcription))

    context = {
        "vo_titel":      os.path.basename(output_file),
        "transcription": transcription,
    }
    logger.debug("  Context:       " + str({k:v for (k, v) in context.items() if k != "transcription"}))

    template_loader = jinja2.FileSystemLoader(searchpath="./templates")
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template("vo_index.html")
    
    output_html = template.render(context)
    options = {
        "page-size": "A4",
        "margin-top": "15mm",
        "margin-right": "15mm",
        "margin-bottom": "15mm",
        "margin-left": "15mm",
    }
    if page_numbers: options["footer-right"] = "[page] / [topage]"
    logger.debug("  Options:       " + str(options))

    pdfkit.from_string(output_html, output_file, options=options)
    logger.info(f"Generated PDF for '{os.path.basename(output_file)}' at '{output_file}'")


def get_all_vo_data(path = None, link = None):
    if path is not None:
        logger.info("Trying to load VO-Data from file: " + path)
        if not os.path.isfile(path):
            logger.error("VO-data file is not a file or doesn't exist: " + path)

        try:
            with open(path, "r", encoding="UTF-8") as f:
                vo_data = json.load(f)
                return vo_data["search-results"]["result"]
        except Exception as e:
            logger.error("Could not load VO-data from file: " + path)

    if link is not None:
        logger.info("Trying to load VO-data from link: " + link)
        try:
            response = requests.get(link)
            vo_data = response.json()
            return vo_data["search-results"]["result"]
        except Exception as e:
            logger.error("Could not load VO-data from link: " + link)
    
    logger.info("Could not load VO-data from file or link. Returning None.")
    return None


def get_vo_data(lecture_map, lecture_index, all_vo_data):
    if lecture_map is None or len(lecture_map) <= 0:
        return None

    for i, j in lecture_map:
        if i == lecture_index and j <= len(all_vo_data):
            return all_vo_data[-j]

    return None


if __name__ == "__main__":
    # Setup Argparse
    parser = argparse.ArgumentParser(description='Transcribe audio files to text')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('-p', '--data-path', help='path to the file where the VO-data is stored (should be formatted like this: https://ustream.univie.ac.at/search/episode.json?limit=200&offset=0&sid=761d2c76-498c-4135-980e-add6660f5ca6), this path is not influenced by the -i/--input-folder argument')
    group.add_argument('-l', '--data-link', help='link to the VO-Data of u:space (f.E. https://ustream.univie.ac.at/search/episode.json?limit=200&offset=0&sid=761d2c76-498c-4135-980e-add6660f5ca6)')

    parser.add_argument('-t', '--lecture-map', nargs=2, type=int, action='append', help='mapping of the transcription files to the VO-Data (f.E. 1 2 means that the first transcription file is mapped to the second lecture in the VO-Data) if not set, the PDF will have no VO-Data, also both indexes start from 1 (not from 0)')
    parser.add_argument('-i', '--input-folder', default='.', help='all transcription paths will be relativ to this path')
    parser.add_argument('-o', '--output-folder', default='.', help='outputfolder where the pdf shall be stored')
    parser.add_argument('-n', '--page-numbers', action='store_true', help='determines if page numbers shall be added to the pdfs')
    parser.add_argument('transcriptions', nargs='+', help='paths to the transcription files that shall be converted to PDFs')


    # args = parser.parse_args(["--help"])
    # args = parser.parse_args("-p data.json -t 1 2 -t 2 3 -t 3 4 -t 4 5 -i output -o output -n".split()+["2. Aufzeichnung vom 20.12.2022.mp3.txt", "3. Aufzeichnung vom 21.12.2022.mp3.txt", "4. Aufzeichnung vom 11.01.2023.mp3.txt", "5. Aufzeichnung vom 12.01.2023.mp3.txt"])
    args = parser.parse_args()


    # Check if input and output folder exist
    if not os.path.isdir(args.input_folder):
        parser.error("Input folder does not exist: " + args.input_folder)
    if not os.path.isdir(args.output_folder):
        parser.error("Output folder does not exist: " + args.output_folder)


    # Setup logging
    logger = logging.getLogger("PDF-Transcribe.log")
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(os.path.join(args.output_folder, "PDF-Transcribe.log"))
    ch = logging.StreamHandler()
    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)

    logger.warning("Starting script")
    logger.info("Input folder:  " + args.input_folder)
    logger.info("Output folder: " + args.output_folder)
    logger.info("Transcriptions: " + str(args.transcriptions))
    logger.info("Page numbers:  " + str(args.page_numbers))


    # Reading VO-Data
    all_vo_data = get_all_vo_data(path=args.data_path, link=args.data_link)


    # Convert to PDFs
    input_paths, output_paths = [], []
    for index, x in enumerate(args.transcriptions, 1):
        path = os.path.join(args.input_folder, x)
        if not os.path.isfile(path):
            logger.error("Transcription file does not exist or is not a file: " + path)
            continue

        input_paths.append((index, path))
        output_paths.append(os.path.join(args.output_folder, x + ".pdf"))


    if all_vo_data:
        logger.info("Successfully loaded VO-data. Converting with VO-data")
        for (index, input), output in zip(input_paths, output_paths):
            logger.info("Converting to PDF: " + input)
            with open(input, "r", encoding="UTF-8") as f:
                transcription = f.read()

            vo_data = get_vo_data(lecture_map=args.lecture_map, lecture_index=index, all_vo_data=all_vo_data)
            if vo_data:
                convert_to_PDF_vo_data(transcription=transcription, output_file=output, vo_data=vo_data, page_numbers=args.page_numbers)
            else:
                convert_to_PDF(transcription=transcription, output_file=output, page_numbers=args.page_numbers)
            logger.info("Done converting to PDF: " + output)


    else:
        logger.info("VO-data not given or could not be loaded. Converting without VO-data")
        for input, output in zip(input_paths, output_paths):
            logger.info("Converting to PDF: " + input)

            with open(input, "r", encoding="UTF-8") as f:
                transcription = f.read()

            convert_to_PDF(transcription=transcription, output_file=output, page_numbers=args.page_numbers)
            logger.info("Done converting to PDF: " + output)


    logger.warning("Finished script")
        
