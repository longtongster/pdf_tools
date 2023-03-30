"""
This module/script allows the merger of several pdf files in one pdf.

The script numbers the each page of the merged contents and adds a bookmark for each file that was merged.

A flag can be set by the user to add blank page between each pdf file that is merged.

Code related to the reportlab library was taken from the following reference:
https://realpython.com/creating-modifying-pdf/
"""
import os
from pathlib import Path
from PyPDF2 import PdfReader, PdfWriter, PdfMerger
from argparse import ArgumentParser

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import grey


def create_page_pdf(num: int, tmp: str, text: str):
    """
    This function creates an empty pdf with only a page number at the bottom and saves
    the result in tmp
    :param num: an integer that determines the number of pages to create in the pdf
    :param tmp: filename used to save the resulting pdf
    :param text: footer text to be added to the bottom of each page
    """
    c = canvas.Canvas(tmp, pagesize=A4)
    for i in range(1, num + 1):
        c.setFont("Times-Roman", 11)
        c.setFillColor(grey)
        # writing footer text to the bottom middle of the page
        c.drawString((210 // 2) * mm - 20 * mm, 4 * mm, text + f" page {i} of {num}")
        c.showPage()
    c.save()


def add_page_numbers(pdf_path: str, new_path: str, text: str, bookmarks: list):
    """
    Add page numbers, a footer and bookmarks to a pdf, saves the result to a new pdf
    :param pdf_path: source pdf
    :param new_path: name of destination pdf
    :param text: footer text
    :param bookmarks: list of tuples, each tuple contains the page number and label for a bookmark
    """
    tmp = "__tmp.pdf"

    writer = PdfWriter()
    # 1. Create a reader object for the pdf to which we want to add page numbers
    with open(pdf_path, "rb") as fr:
        reader = PdfReader(fr)
        n = len(reader.pages)

        # 2. create new PDF that contains a footer and page numbers
        create_page_pdf(n, tmp, text)

        # 3. create a second reader for the new PDF
        with open(tmp, "rb") as ftmp:
            number_pdf = PdfReader(ftmp)
            # iterarte pages
            for p in range(n):
                # .pages is PageObject represents a single page within a PDF file
                page = reader.pages[p]
                number_layer = number_pdf.pages[p]
                # merge number page with the page containing the footer and page number in one page
                page.merge_page(number_layer)
                writer.add_page(page)

            for p_num, label in bookmarks:
                writer.add_outline_item(title=label, page_number=p_num)

            # write result
            if len(writer.pages) > 0:
                with open(new_path, "wb") as f:
                    writer.write(f)
        # remove the pdf that just contains the page numbers
        # this is just a 'helper pdf'
        os.remove(tmp)


def create_blank_page(dst_pdf_path: str):
    """
    Creates a blank pdf page of A4 format and writes it to disk
    :param dst_pdf_path: the file path for the newly created blank pdf
    """
    with open(dst_pdf_path, "wb") as f:
        writer = PdfWriter()
        writer.add_blank_page(210 * mm, 279 * mm)
        writer.write(f)


def merge_pdf_list(src_dir: str, dst_pdf_path: str, with_blank: bool = False):
    """
    merges a list of pdfs to one big pdf and writes the result to dst_pdf_path.

    It also add bookmarks however these seem to be overwritten when we add page numbers in a separate step.
    To fix this we return a list tuples where each tuple contains the page number and label for a bookmarks.
    These can be provided a input to the add_page_numbers function.

    :param src_dir: source directory that contains the pdfs to merge
    :param dst_pdf_path: destination file path to save the merged pdfs
    :param with_blank: if provided the function will create a blank page and add it between each pdf that is merged
    :returns bookmarks: a list of tuples where is tuple contains the page number and label for a bookmark.
    """

    bookmarks = list()
    input_path = Path(src_dir)
    merger = PdfMerger()   # instantiate a pdf writer

    # if with_blank = True create a temporary blank pdf
    if with_blank:
        tmp_path = "--tmp.pdf"
        create_blank_page(tmp_path)

    # go over each pdf in the src_dir and append it to the merger
    for path in input_path.glob("*.pdf"):
        # create a list of tuples for the bookmarks:
        bookmarks.append((len(merger.pages), path.name))

        with open(path, "rb") as f:
            # the second argument sets a book mark
            merger.append(f, str(path.name))
            # if there is a blank_path add a blank page
            if with_blank:
                with open(tmp_path, "rb") as fb:
                    merger.append(fb)
                    fb.close()
    # write all pdfs in the merger to dst_pdf_path
    with open(dst_pdf_path, "wb") as fw:
        merger.write(fw)

    # delete the blank page to keep a clean working space
    if with_blank:
        os.remove(tmp_path)

    return bookmarks


def parser():
    parser = ArgumentParser()
    parser.add_argument("--input-dir", required=True, type=str,
                        help="directory path that contains the pdfs to be converted")

    parser.add_argument("--output-path", required=True, type=str,
                        help="file path to which file with merged pdfs should be written")

    parser.add_argument("--footer-text", required=True, type=str,
                        help="text that will be added to the bottom of each page")

    parser.add_argument("--add-blank", type=bool, default=True,
                        help="flag to determine if you want a blank page between each document")

    return parser


if __name__ == "__main__":

    parser = parser()
    args = parser.parse_args()
    print("[INFO] The following arguments are parsed from the argparse:")
    print(args)

    # merge all pdfs and store in a temporary file
    tmp_path = "./tmp.pdf"
    print(f"[INFO] merging all pdf in the directory {args.input_dir} and saving the result to {tmp_path}")
    bookmarks = merge_pdf_list(args.input_dir, tmp_path, with_blank=args.add_blank)

    # add page numbers and store in user provided location then delete the temporary file
    print(f"[INFO] numbering the pages and adding bookmarks in the file {tmp_path} and saving to {args.output_path}  ")
    add_page_numbers(tmp_path, args.output_path, args.footer_text, bookmarks)
    os.remove(tmp_path)

    print("[INFO] script finished succesfully ...")
