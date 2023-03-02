import argparse
import logging
import os
from datetime import datetime, timedelta

import jinja2
import pdfkit


logger = logging.getLogger("VO-Transcriber")


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
    logger.debug("  Options:       %s", str(options))

    pdfkit.from_string(output_html, output_file, options=options)
    logger.info("Generated PDF for '%s' at '%s'", os.path.basename(output_file), output_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Converts a transcription to a PDF")

    parser.add_argument("--with-vo-data", action="store_true", help="indicates that the transcription is part of a VO")
    parser.add_argument("--autor", type=str, help="Autor of the VO")
    parser.add_argument("--beitragende", type=str, help="Contributors of the VO")
    parser.add_argument("--length", type=int, help="Length of the VO (as milliseconds)")
    parser.add_argument(
        "--recorded-on",
        type=str,
        help="Date and time the VO was recorded in format: YYYY-MM-DDTHH:MM:SS+-TZ' (example: 2020-01-01T12:00:00+01:00)",
    )
    parser.add_argument("--series-name", type=str, help="Name of the series the VO is part of")
    parser.add_argument("--link", help="Link to the VO (is intended to be a link to the raw MP4 file)")

    #   %Y-%m-%dT%H:%M:%S%Z

    parser.add_argument("--vo-title", type=str, required=True, help="Title of the VO")
    parser.add_argument("--transcription", type=str, required=True, help="File path to the transcription of the VO")
    parser.add_argument("--page-numbers", action="store_true", help="Whether to add page numbers to the PDF")
    parser.add_argument("out_path", type=str, help="Path to the output file")

    args = parser.parse_args()

    if not os.path.isfile(args.transcription):
        parser.error("Transcription file does not exist")

    if args.with_vo_data:
        if args.autor is None:
            parser.error("--autor is required when using --with-vo-data")
        if args.beitragende is None:
            parser.error("--beitragende is required when using --with-vo-data")
        if args.length is None:
            parser.error("--length is required when using --with-vo-data")
        if args.recorded_on is None:
            parser.error("--recorded-on is required when using --with-vo-data")
        if args.series_name is None:
            parser.error("--series-name is required when using --with-vo-data")
        if args.link is None:
            parser.error("--link is required when using --with-vo-data")

        with open(args.transcription, "r", encoding="UTF-8") as f:
            transcription = f.read()

        convert_to_PDF_vo_data(
            output_file=args.out_path,
            vo_title=args.vo_title,
            autor=args.autor,
            beitragende=args.beitragende,
            length=timedelta(milliseconds=int(args.length)),
            recorded_on=datetime.strptime(args.recorded_on, "%Y-%m-%dT%H:%M:%S%Z"),
            series_name=args.series_name,
            link=args.link,
            transcription=transcription,
            page_numbers=args.page_numbers,
        )
    else:
        with open(args.transcription, "r", encoding="UTF-8") as f:
            transcription = f.read()

        convert_to_PDF(
            transcription=transcription,
            output_file=args.out_path,
            page_numbers=args.page_numbers,
        )
