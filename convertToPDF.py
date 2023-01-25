import argparse
import json
import logging
import os
from datetime import datetime, timedelta

import jinja2
import pdfkit
import requests


logger = logging.getLogger("VOs-Transcribe")


def convert_to_PDF_vo_data(
    output_file: str,
    vo_title: str,
    autor: str,
    beitragende: str,
    length: timedelta,
    recorded_on: datetime,
    series_name: str,
    link: str,
    transcription: str,
    page_numbers=False,
):
    """
    Generates a PDF with the given data and saves it to the given path.
    :param output_file:     Path to the output file (should end with .pdf)
    :param vo_title:        Title of the VO
    :param autor:           Autor of the VO
    :param beitragende:     Contributors of the VO
    :param length:          Length of the VO (as timedelta)
    :param recorded_on:     Date and time the VO was recorded (as datetime)
    :param series_name:     Name of the series the VO is part of
    :param link:            Link to the VO (is intended to be a link to the raw MP4 file)
    :param transcription:   Transcription of the VO
    :param page_numbers:    Whether to add page numbers to the PDF
    """
    logger.info("Generating PDF (with VO-Data) for '%s'", vo_title)
    logger.debug("  Outputfile:    %s", output_file)
    logger.debug("  Page numbers:  %s", str(page_numbers))
    # logger.debug("  VO-Data:       " + json.dumps(vo_data))
    # logger.debug("  Transcription: " + str(transcription))

    context = {
        "vo_titel": vo_title,
        "autor": autor,
        "beitragende": beitragende,
        "length": str(length),
        "recorded_on": recorded_on.strftime("%d.%m.%Y %H:%M"),
        "series_name": series_name,
        "link": link,
        "transcription": transcription,
    }
    logger.debug("  Context:       %s", str({k: v for (k, v) in context.items() if k != "transcription"}))

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
    if page_numbers:
        options["footer-right"] = "[page] / [topage]"
    logger.debug("  Options:       %s", str(options))

    pdfkit.from_string(output_html, output_file, options=options)
    logger.info("Generated PDF for '%s' at '%s'", vo_title, output_file)


def convert_to_PDF(transcription, output_file, page_numbers=False):
    """
    Generates a PDF with the given transcription and saves it to the given path.
    :param transcription:   Transcription of the VO
    :param output_file:     Path to the output file (should end with .pdf)
    :param page_numbers:    Whether to add page numbers to the PDF
    """
    logger.info("Generating PDF for '%s'", os.path.basename(output_file))
    logger.debug("  Outputfile:    %s", output_file)
    logger.debug("  Page numbers:  %s", str(page_numbers))
    # logger.debug("  Transcription: " + str(transcription))

    context = {
        "vo_titel": os.path.basename(output_file),
        "transcription": transcription,
    }
    logger.debug("  Context:       %s", str({k: v for (k, v) in context.items() if k != "transcription"}))

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
    if page_numbers:
        options["footer-right"] = "[page] / [topage]"
    logger.debug("  Options:       " + str(options))

    pdfkit.from_string(output_html, output_file, options=options)
    logger.info("Generated PDF for '%s' at '%s'", os.path.basename(output_file), output_file)
